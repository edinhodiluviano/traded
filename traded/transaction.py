import datetime as dt

import sqlalchemy as sa
from pydantic import condecimal, validator
from fastapi import APIRouter, HTTPException

from .dependencies import sess
from . import db
from ._classes import NoExtraModel


router = APIRouter(
    prefix="/transaction",
    tags=["transaction"],
)


class EntryCreate(NoExtraModel):
    account_id: int
    value: condecimal(decimal_places=10)
    asset_id: int
    quantity: condecimal(decimal_places=10)

    @validator("value")
    def value_should_be_not_zero(cls, value):
        if value == 0:
            raise ValueError("Value should be not zero")
        return value

    @validator("quantity")
    def quantity_should_be_not_zero(cls, quantity):
        if quantity == 0:
            raise ValueError("Quantity should be not zero")
        return quantity


class TransactionCreate(NoExtraModel):
    datetime: dt.datetime
    description: str
    entries: list[EntryCreate]
    fund_id: int

    @validator("entries")
    def entries_should_be_balanced(cls, entries):
        values = [entry.value for entry in entries]
        if sum(values) != 0:
            raise ValueError("Entries are not balanced")
        return entries

    @validator("entries")
    def entries_list_should_have_at_least_one_entry(cls, entries):
        if len(entries) == 0:
            raise ValueError("A transaction should have at least one entry")
        return entries


class Entry(EntryCreate):
    id: int
    datetime: dt.datetime
    transaction_id: int
    cancel: bool
    fund_id: int


class Transaction(TransactionCreate):
    id: int
    entries: list[Entry]
    timestamp: dt.datetime
    datetime: dt.datetime
    value: condecimal(decimal_places=10)
    cancel: bool
    fund_id: int


@router.post("", response_model=Transaction)
def create_transaction(
    transaction: TransactionCreate,
    session: sa.orm.Session = sess,
):
    entries = [
        db.models.Entry(
            **entry.dict(),
            datetime=transaction.datetime,
            fund_id=transaction.fund_id,
        )
        for entry in transaction.entries
    ]
    entries_value = sum([entry.value for entry in entries if entry.value > 0])

    transaction_db = db.models.Transaction(
        datetime=transaction.datetime,
        timestamp=dt.datetime.utcnow(),
        value=entries_value,
        description=transaction.description,
        entries=entries,
        fund_id=transaction.fund_id,
    )
    session.add(transaction_db)
    db.main.try_to_commit(session)
    session.refresh(transaction_db)
    return transaction_db


@router.get("", response_model=list[Transaction])
def get_transaction(session: sa.orm.Session = sess):
    query = session.query(db.models.Transaction)
    transactions = query.all()
    return transactions


@router.delete("/{transaction_id}", response_model=Transaction)
def cancel_transaction(
    transaction_id: int,
    session: sa.orm.Session = sess,
):
    "Creates a transaction that reverse the original"

    # find the original transaction
    transaction = session.query(db.models.Transaction).get(transaction_id)
    if transaction is None:
        msg = f"Transaction {transaction_id=} not found"
        raise HTTPException(status_code=404, detail=msg)

    # cancel it and create reverse entries
    transaction.cancel = True
    entries = []
    for n in range(len(transaction.entries)):
        original_entry = transaction.entries[n]
        original_entry.cancel = True
        new_entry = EntryCreate(
            account_id=original_entry.account_id,
            value=-original_entry.value,
            asset_id=original_entry.asset_id,
            quantity=-original_entry.quantity,
        )
        new_entry_db = db.models.Entry(
            **new_entry.dict(),
            datetime=transaction.datetime,
            cancel=True,
            fund_id=transaction.fund_id,
        )
        entries.append(new_entry_db)

    # create the reverse transaction
    canceling = db.models.Transaction(
        timestamp=dt.datetime.utcnow(),
        datetime=transaction.datetime,
        value=transaction.value,
        description=f"Cancel: {transaction_id}",
        entries=entries,
        cancel=True,
        fund_id=transaction.fund_id,
    )

    # persist and return
    session.add(canceling)
    db.main.try_to_commit(session)
    return canceling
