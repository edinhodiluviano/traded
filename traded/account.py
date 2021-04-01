import pydantic
import sqlalchemy as sa

from .database import Base
from ._classes import NoExtraModel, OrmModel


class _AccountBase(NoExtraModel):
    name: str
    postable: bool
    is_active: bool = True
    parent_id: int = None


class AccountCreate(_AccountBase):
    pass


class Account(_AccountBase, OrmModel):
    id: int
    children: list
    parent_id: int = None
    parent: "Account" = None

    @pydantic.validator("children")
    def children_must_be_list_of_accounts(cls, v):
        children = [Account.from_orm(o) for o in v]
        return children


Account.update_forward_refs()


class AccountDb(Base):
    __tablename__ = "account"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    name = sa.Column(sa.String, unique=True, index=False, nullable=False)
    postable = sa.Column(sa.Boolean, nullable=False)
    is_active = sa.Column(sa.Boolean, default=True, nullable=False)
    parent_id = sa.Column(
        sa.Integer, sa.ForeignKey("account.id"), nullable=True
    )
    children = sa.orm.relationship("AccountDb")

    def __repr__(self):
        return (
            f"<Account: id={self.id}, name={self.name}, "
            f"children={self.children}>"
        )


@Account.returner
def get_by_id(sess: sa.orm.Session, account_id: int):
    query = sess.query(AccountDb).filter(AccountDb.id == account_id)
    return query.first()


@Account.returner
def get(sess: sa.orm.Session, offset: int = 0, limit: int = 0):
    query = sess.query(AccountDb)
    if offset > 0:
        query = query.offset(offset)
    if limit > 0:
        query = query.limit(limit)
    return query.all()


@Account.returner
def insert(sess: sa.orm.Session, account: AccountCreate):
    acc = AccountDb(**account.dict())
    sess.add(acc)
    sess.commit()
    return acc


@Account.returner
def create_default_coa(sess: sa.orm.Session):
    """
    Current Chart of Accounts:
    root
        Assets
            cash
            receivables
            inventory
        Liabilities
            ac. payables
            shares issued
            retained earnings
        Income/Expense
            trade
            interest
            Fees
                broker
                administration
            tax
            other
    """

    root = AccountCreate(name="root", postable=False)
    root = insert(sess, root)

    assets = AccountCreate(name="Assets", postable=False, parent_id=root.id)
    assets = insert(sess, assets)

    cash = AccountCreate(name="Cash", postable=True, parent_id=assets.id)
    cash = insert(sess, cash)

    recv = AccountCreate(
        name="Receivables", postable=True, parent_id=assets.id
    )
    recv = insert(sess, recv)

    inventory = AccountCreate(
        name="Inventory", postable=True, parent_id=assets.id
    )
    inventory = insert(sess, inventory)

    liab = AccountCreate(name="Liabilities", postable=False, parent_id=root.id)
    liab = insert(sess, liab)

    payb = AccountCreate(name="Payables", postable=True, parent_id=liab.id)
    payb = insert(sess, payb)

    shares = AccountCreate(
        name="Shares Issued", postable=True, parent_id=liab.id
    )
    shares = insert(sess, shares)

    earns = AccountCreate(
        name="Retained Earnings", postable=True, parent_id=liab.id
    )
    earns = insert(sess, earns)

    income = AccountCreate(
        name="Income/Expenses", postable=False, parent_id=root.id
    )
    income = insert(sess, income)

    trade = AccountCreate(name="Trade", postable=True, parent_id=income.id)
    trade = insert(sess, trade)

    pmt = AccountCreate(name="Interest", postable=True, parent_id=income.id)
    pmt = insert(sess, pmt)

    fees = AccountCreate(name="Fees", postable=False, parent_id=income.id)
    fees = insert(sess, fees)

    broker = AccountCreate(name="Broker", postable=True, parent_id=fees.id)
    broker = insert(sess, broker)

    adm = AccountCreate(
        name="Administration", postable=True, parent_id=fees.id
    )
    adm = insert(sess, adm)

    tax = AccountCreate(name="Taxes", postable=True, parent_id=income.id)
    tax = insert(sess, tax)

    other = AccountCreate(name="Other", postable=True, parent_id=income.id)
    other = insert(sess, other)

    return [
        root,
        assets,
        cash,
        recv,
        inventory,
        liab,
        payb,
        shares,
        earns,
        income,
        trade,
        pmt,
        fees,
        broker,
        adm,
        tax,
        other,
    ]
