import datetime as dt
from decimal import Decimal

import pydantic
import sqlalchemy as sa

from .database import Base
from ._classes import NoExtraModel, OrmModel
from .asset import Asset
from .account import Account


class _EntryBase(NoExtraModel):
    datetime: dt.datetime
    account: Account
    value: Decimal
    asset_id: int
    qnt: Decimal


class EntryCreate(_EntryBase):
    pass


class Entry(_EntryBase, OrmModel):
    id: int
    transaction_id: dt.datetime
    asset: Asset


class EntryDb(Base):
    __tablename__ = "entry"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    datetime = sa.Column(sa.DateTime, nullable=False, index=True)
    value = sa.Numeric(precision=20, scale=10, asdecimal=True)
    qnt = sa.Numeric(precision=20, scale=10, asdecimal=True)

    asset_id = sa.Column(
        sa.Integer, sa.ForeignKey("asset.id"), nullable=False, index=True
    )
    asset = sa.orm.relationship("AssetDb")

    transaction_id = sa.Column(
        sa.Integer, sa.ForeignKey("transaction.id"), nullable=False
    )

    account_id = sa.Column(
        sa.Integer, sa.ForeignKey("account.id"), nullable=False, index=True
    )
    account = sa.orm.relationship("AccountDb")


class _TransactionBase(NoExtraModel):
    datetime: dt.datetime
    description: str


class TransactionCreate(_TransactionBase):
    entries: list[EntryCreate]

    @pydantic.validator("entries")
    def entries_must_sum_zero(cls, entries):
        values = [e.value for e in entries]
        if sum(values) != 0:
            msg = (
                "Transaction entries are not balanced. "
                "Total value must sum zero"
            )
            raise ValueError(msg)
        return entries

    @pydantic.validator("entries")
    def entries_should_have_at_least_one_element(cls, entries):
        if len(entries) == 0:
            msg = "Transaction must have at least one entry attached to it"
            raise ValueError(msg)
        return entries

    def calc_value(self):
        return sum([abs(e.value) for e in self.entries]) / 2


class Transaction(_TransactionBase, OrmModel):
    id: int
    value: Decimal
    timestamp: dt.datetime
    entries: list[Entry]

    @pydantic.validator("entries")
    def entries_should_have_at_least_one_element(cls, entries):
        if len(entries) == 0:
            msg = "Transaction must have at least one entry attached to it"
            raise ValueError(msg)
        return entries


class TransactionDb(Base):
    __tablename__ = "transaction"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    datetime = sa.Column(sa.DateTime, index=True, nullable=False)
    timestamp = sa.Column(sa.DateTime, nullable=False)
    description = sa.Column(sa.String, nullable=True)
    value = sa.Numeric(precision=20, scale=10, asdecimal=True)

    entries = sa.orm.relationship("EntryDb", lazy="immediate")


@Transaction.returner
def insert(
    sess: sa.orm.Session, transaction: TransactionCreate
) -> Transaction:

    entries = [
        EntryDb(
            datetime=transaction.datetime,
            value=e.value,
            qnt=e.qnt,
            asset_id=e.asset_id,
            account_id=e.account.id,
        )
        for e in transaction.entries
    ]

    transaction_db = TransactionDb(
        datetime=transaction.datetime,
        timestamp=dt.datetime.utcnow(),
        description=transaction.description,
        value=transaction.calc_value(),
        entries=entries,
    )
    sess.add(transaction_db)
    sess.commit()
    sess.refresh(transaction_db)

    return transaction_db
