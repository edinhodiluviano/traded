import sqlalchemy as sa


Base = sa.ext.declarative.declarative_base()


class Account(Base):
    __tablename__ = "account"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    name = sa.Column(sa.String, unique=True, index=True, nullable=False)
    postable = sa.Column(sa.Boolean, nullable=False)
    is_active = sa.Column(sa.Boolean, default=True, nullable=False)
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
    is_active = sa.Column(sa.Boolean, default=True, nullable=False)
    type = sa.Column(sa.String, unique=False, index=True, nullable=False)

    # type specific fields
    # bond
    bond_expiration = sa.Column(sa.DateTime, index=False, nullable=True)
    bond_value = sa.Numeric(precision=20, scale=10, asdecimal=True)
