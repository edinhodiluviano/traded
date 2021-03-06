import sqlalchemy as sa
import sqlalchemy.ext.declarative


Base = sa.ext.declarative.declarative_base()


class Account(Base):
    __tablename__ = "account"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    name = sa.Column(sa.String, unique=True, index=True, nullable=False)
    parent_id = sa.Column(
        sa.Integer, sa.ForeignKey("account.id"), nullable=True
    )

    parent = sa.orm.relationship("Account")


class Asset(Base):
    """
    The retricted fields are defined in traded.asset enum classes
    traded.asset.AssetTypes:
        currency
        stock
        fund
        bond
    """

    __tablename__ = "asset"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    name = sa.Column(sa.String, unique=True, index=True, nullable=False)
    description = sa.Column(sa.String, index=False, nullable=False)
    is_active = sa.Column(sa.Boolean, default=True, index=True, nullable=False)
    type = sa.Column(sa.String, unique=False, index=True, nullable=False)

    # type specific fields
    # bond
    bond_expiration = sa.Column(sa.DateTime, index=False, nullable=True)
    bond_value = sa.Column(
        sa.Numeric(precision=20, scale=10, asdecimal=True),
        index=False,
        nullable=True,
    )


class Entry(Base):
    "A simple journal entry"

    __tablename__ = "entry"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    datetime = sa.Column(sa.DateTime, index=True, nullable=False)
    account_id = sa.Column(
        sa.Integer, sa.ForeignKey("account.id"), nullable=False, index=True
    )
    value = sa.Column(
        sa.Numeric(precision=20, scale=10, asdecimal=True),
        index=False,
        nullable=False,
    )
    asset_id = sa.Column(
        sa.Integer, sa.ForeignKey("asset.id"), nullable=False, index=True
    )
    quantity = sa.Column(
        sa.Numeric(precision=20, scale=10, asdecimal=True),
        index=False,
        nullable=False,
    )
    cancel = sa.Column(sa.Boolean, default=False, index=True, nullable=False)
    fund_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("fund.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    transaction_id = sa.Column(
        sa.Integer, sa.ForeignKey("transaction.id"), nullable=False, index=True
    )


class Transaction(Base):
    "A transaction comprises multiple entries"

    __tablename__ = "transaction"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    timestamp = sa.Column(sa.DateTime, index=True, nullable=False)
    datetime = sa.Column(sa.DateTime, index=True, nullable=False)
    value = sa.Column(
        sa.Numeric(precision=20, scale=10, asdecimal=True),
        index=False,
        nullable=False,
    )
    description = sa.Column(sa.String, index=False, nullable=False)
    cancel = sa.Column(sa.Boolean, default=False, index=True, nullable=False)
    fund_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("fund.id"),
        nullable=False,
        index=True,
    )

    entries = sa.orm.relationship("Entry", cascade="all, delete-orphan")


class Fund(Base):
    __tablename__ = "fund"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    name = sa.Column(sa.String, unique=True, index=True, nullable=False)
    temporary = sa.Column(sa.Boolean, index=False, nullable=False)
    asset_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("asset.id"),
        nullable=False,
        index=False,
    )
    asset = sa.orm.relationship("Asset")

    transactions = sa.orm.relationship(
        "Transaction",
        cascade="all, delete-orphan",
    )
