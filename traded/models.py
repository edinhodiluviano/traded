from decimal import Decimal
from enum import Enum

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
    ) -> "Account":

        a = cls(
            name=name,
            parent=parent,
            entry=entry,
            active=active,
        )
        return a


class AssetType(str, Enum):
    currency = "currency"


class Asset(Base):
    __tablename__ = "asset"
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    name = sa.Column(sa.String, unique=True, index=True, nullable=False)
    type = sa.Column(sa.types.Enum(AssetType), index=True, nullable=False)
    price_asset_id = sa.Column(
        sa.Integer, sa.ForeignKey("asset.id"), nullable=True, index=True
    )

    price_asset = sa.orm.relationship("Asset", remote_side=[id])

    @classmethod
    def get_from_name(cls, name: str, session: sa.orm.Session) -> "Asset":
        """Return an asset object from its name."""
        stmt = sa.select(cls).where(cls.name == name)
        result = session.scalar(stmt)
        return result


class EntryLine(Base):
    __tablename__ = "entry_line"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    account_id = sa.Column(sa.Integer, sa.ForeignKey("account.id"), index=True)
    entry_id = sa.Column(sa.Integer, sa.ForeignKey("entry.id"), index=True)
    value = sa.Column(sa.Numeric(12, 6), nullable=False)
    asset_id = sa.Column(sa.Integer, sa.ForeignKey("asset.id"), index=True)
    quantity = sa.Column(sa.Numeric(12, 6), nullable=False)

    asset = sa.orm.relationship("Asset")

    @classmethod
    def new(
        cls,
        *,
        account: Account,
        value: Decimal,
        asset: Asset,
        quantity: Decimal,
    ) -> "EntryLine":
        o = cls(
            account_id=account.id, value=value, asset=asset, quantity=quantity
        )
        return o

    @classmethod
    def from_dict(cls, /, d: dict):
        o = cls.new(**d)
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
