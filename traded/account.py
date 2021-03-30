import sqlalchemy as sa

from .database import Base
from ._classes import NoExtraModel, OrmModel


class _AccountBase(NoExtraModel):
    name: str
    postable: bool
    is_active: bool = True


class AccountCreate(_AccountBase):
    pass


class Account(_AccountBase, OrmModel):
    id: int


class AccountDb(Base):
    __tablename__ = "account"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    name = sa.Column(sa.String, unique=False, index=False, nullable=False)
    postable = sa.Column(sa.Boolean, nullable=False)
    is_active = sa.Column(sa.Boolean, default=True, nullable=False)
#     parent_id = sa.Column(sa.Integer, sa.ForeignKey("account.id"))
#     parent = sa.orm.relationship("Account")

#    children = sa.orm.relationship(
#        "Account",
#        backref=sa.orm.backref("parent", remote_side=[id]),
#    )


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
    sess.refresh(acc)
    return acc
