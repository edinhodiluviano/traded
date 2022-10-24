from decimal import Decimal

import sqlalchemy as sa
import sqlalchemy.ext.declarative

Base = sa.ext.declarative.declarative_base()


class Account(Base):
    __tablename__ = "account"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    parent_id = sa.Column(
        sa.Integer, sa.ForeignKey("account.id"), nullable=True, index=True
    )
    name = sa.Column(sa.String, unique=False, index=True, nullable=False)
    entry = sa.Column(sa.Boolean, index=False, nullable=False)
    active = sa.Column(sa.Boolean, index=True, nullable=False)

    @classmethod
    def new(
        cls,
        *,
        name: str,
        parent: "Account" = None,
        entry: bool = True,
        active: bool = True,
    ) -> "Account":
        parent_id = None
        if parent:
            parent_id = parent.id
        a = cls(
            name=name,
            parent_id=parent_id,
            entry=entry,
            active=active,
        )
        return a


class EntryLine(Base):
    __tablename__ = "entry_line"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    account_id = sa.Column(sa.Integer, sa.ForeignKey("account.id"), index=True)
    entry_id = sa.Column(sa.Integer, sa.ForeignKey("entry.id"), index=True)
    value = sa.Column(sa.Numeric(12, 6), nullable=False)

    @classmethod
    def new(
        cls,
        *,
        account: Account,
        value: Decimal,
    ) -> "EntryLine":
        o = cls(account_id=account.id, value=value)
        return o

    @classmethod
    def from_dict(cls, /, d: dict):
        o = cls.new(account=d["account"], value=d["value"])
        return o


class Entry(Base):
    __tablename__ = "entry"

    id = sa.Column(sa.Integer, primary_key=True, index=True)

    entries = sa.orm.relationship("EntryLine")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.check_balance()

    def check_balance(self):
        balance = sum([e.value for e in self.entries])
        if balance != 0:
            msg = f"Entries should be balanced but {balance=}"
            raise ValueError(msg)

    @classmethod
    def new(cls, *, entries: list) -> "Entry":
        new_entry = cls(entries=[])
        for entry_line in entries:
            if isinstance(entry_line, dict):
                entry_line = EntryLine.from_dict(entry_line)
            new_entry.entries.append(entry_line)
        return new_entry
