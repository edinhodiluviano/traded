import sqlalchemy as sa


Base = sa.ext.declarative.declarative_base()


class ReprMixin:
    def __repr__(self):
        r = f"<DB:{self.__class__.__name__}: name={self.name}; id={self.id}>"
        return r


class Account(Base, ReprMixin):
    __tablename__ = "account"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    name = sa.Column(sa.String, unique=True, index=True, nullable=False)
    postable = sa.Column(sa.Boolean, nullable=False)
    is_active = sa.Column(sa.Boolean, default=True, nullable=False)
    parent_id = sa.Column(
        sa.Integer, sa.ForeignKey("account.id"), nullable=True
    )

    parent = sa.orm.relationship("Account")


class Asset(Base, ReprMixin):
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
    transaction_id = sa.Column(
        sa.Integer, sa.ForeignKey("transaction.id"), nullable=False, index=True
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
    entries = sa.orm.relationship("Entry", lazy="immediate")
