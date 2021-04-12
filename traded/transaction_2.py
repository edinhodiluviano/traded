import datetime as dt
import traceback as tb

import sqlalchemy as sa
from pydantic import condecimal, validator
from fastapi import APIRouter, Depends, HTTPException

from .dependencies import get_session
from .db import models
from ._classes import NoExtraModel


router = APIRouter()


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


class TransactionCreate(NoExtraModel):
    datetime: dt.datetime
    description: str
    entries: list[EntryCreate]

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


class Transaction(TransactionCreate):
    id: int
    entries: list[Entry]
    timestamp: dt.datetime
    datetime: dt.datetime
    value: condecimal(decimal_places=10)


def try_to_commit(session: sa.orm.Session):
    try:
        session.commit()
    except sa.exc.IntegrityError:
        session.rollback()
        raise HTTPException(status_code=422, detail=tb.format_exc(limit=0))


@router.post("/transaction", tags=["transaction"], response_model=Transaction)
def create_transaction(
    transaction: TransactionCreate,
    session: sa.orm.Session = Depends(get_session),
):

    entries = [
        models.Entry(**entry.dict(), datetime=transaction.datetime)
        for entry in transaction.entries
    ]
    entries_value = sum([entry.value for entry in entries if entry.value > 0])

    transaction_db = models.Transaction(
        datetime=transaction.datetime,
        timestamp=dt.datetime.utcnow(),
        value=entries_value,
        description=transaction.description,
        entries=entries,
    )
    session.add(transaction_db)
    try_to_commit(session)
    session.refresh(transaction_db)
    return transaction_db
