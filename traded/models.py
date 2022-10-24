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
    balance = sa.Column(sa.Numeric(12, 6), nullable=False)

    parent = sa.orm.relationship("Account", remote_side=[id])
    children = sa.orm.relationship(
        "Account", lazy="joined", join_depth=2, viewonly=True
    )

    @classmethod
    def new(
        cls,
        *,
        name: str,
        parent: "Account" = None,
        entry: bool = True,
        active: bool = True,
        balance: Decimal = 0,
    ) -> "Account":

        a = cls(
            name=name,
            parent=parent,
            entry=entry,
            active=active,
            balance=balance,
        )
        return a

    def change_balance(self, /, diff_value: Decimal):
        """Change balance of account and parents by the diff_value."""
        self.balance += diff_value
        if self.parent is not None:
            self.parent.change_balance(diff_value)


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
        account.change_balance(value)
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
    note = sa.Column(sa.String, unique=False, index=False, nullable=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._check_balance()

    def _check_balance(self):
        balance = sum([e.value for e in self.entries])
        if balance != 0:
            msg = f"Entries should be balanced but {balance=}"
            raise ValueError(msg)

    @classmethod
    def new(cls, *, entries: list, note: str) -> "Entry":
        new_entry = cls(entries=[], note=note)
        for entry_line in entries:
            if isinstance(entry_line, dict):
                entry_line = EntryLine.from_dict(entry_line)
            new_entry.entries.append(entry_line)
        return new_entry
