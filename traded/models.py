import datetime as dt
from decimal import Decimal
from typing import Self

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""


class Account(Base):
    __tablename__ = 'account'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        sa.String(100), unique=True, nullable=False
    )

    parent_id: Mapped[int | None] = mapped_column(
        sa.ForeignKey('accounts.id'), nullable=True
    )

    parent: Mapped[Self | None] = relationship(remote_side=[id])
    children: Mapped[list[Self]] = relationship(
        'Account', back_populates='parent', cascade='all, delete-orphan'
    )

    entries: Mapped[list['Entry']] = relationship(back_populates='account')

    def __repr__(self) -> str:
        return f'Account(id={self.id!r}, name={self.name!r})'


class Asset(Base):
    __tablename__ = 'asset'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    type: Mapped[str] = mapped_column(sa.String(50), nullable=False)

    entries: Mapped[list['Entry']] = relationship(back_populates='asset')

    def __repr__(self) -> str:
        return f'Asset(id={self.id!r}, name={self.name!r}, type={self.type!r})'


class Transaction(Base):
    __tablename__ = 'transaction'

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[dt.datetime] = mapped_column(sa.DateTime, nullable=False)
    description: Mapped[str] = mapped_column(sa.String(255), nullable=False)

    entries: Mapped[list['Entry']] = relationship(
        back_populates='transaction', cascade='all, delete-orphan'
    )

    def __repr__(self) -> str:
        return (
            f'Transaction(id={self.id!r}, date={self.date!r}, '
            f'description={self.description!r})'
        )


class Entry(Base):
    __tablename__ = 'entry'

    id: Mapped[int] = mapped_column(primary_key=True)

    value: Mapped[Decimal] = mapped_column(sa.Numeric(18, 6), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(sa.Numeric(18, 6))

    account_id: Mapped[int] = mapped_column(
        sa.ForeignKey('accounts.id'), nullable=False
    )
    asset_id: Mapped[int] = mapped_column(
        sa.ForeignKey('assets.id'), nullable=False
    )
    transaction_id: Mapped[int] = mapped_column(
        sa.ForeignKey('transactions.id'), nullable=False
    )

    account: Mapped['Account'] = relationship(back_populates='entries')
    asset: Mapped['Asset'] = relationship(back_populates='entries')
    transaction: Mapped['Transaction'] = relationship(back_populates='entries')

    def __repr__(self) -> str:
        return (
            f'Entry(id={self.id!r}, value={self.value!r}, '
            f'account_id={self.account_id!r})'
        )
