from enum import Enum

import sqlalchemy as sa

from .database import Base
from ._classes import NoExtraModel, OrmModel


class AssetTypes(str, Enum):
    currency = "currency"
    stock = "stock"
    fund = "fund"
    option = "option"
    future = "future"
    index = "index"


class _AssetBase(NoExtraModel):
    name: str
    active: bool = True
    type: AssetTypes


class AssetCreate(_AssetBase):
    pass


class Asset(_AssetBase, OrmModel):
    id: int


class AssetDb(Base):
    __tablename__ = "asset"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    name = sa.Column(sa.String, unique=True, index=True, nullable=False)
    active = sa.Column(sa.Boolean, nullable=False, index=True)
    type = sa.Column(sa.String, unique=False, index=True, nullable=False)


@Asset.returner
def get_by_name(sess: sa.orm.Session, name: str):
    query = sess.query(AssetDb).filter(AssetDb.name == name)
    result = query.first()
    return result


@Asset.returner
def get(sess: sa.orm.Session, offset: int = 0, limit: int = 0):
    query = sess.query(AssetDb)
    if offset > 0:
        query = query.offset(offset)
    if limit > 0:
        query = query.limit(limit)
    return query.all()


@Asset.returner
def insert(sess: sa.orm.Session, asset: AssetCreate):
    acc = AssetDb(**asset.dict())
    sess.add(acc)
    sess.commit()
    return acc


@Asset.returner
def edit(sess: sa.orm.Session, asset_id: int, field: str, new_value):
    asset = sess.query(AssetDb).filter(AssetDb.id == asset_id).first()
    setattr(asset, field, new_value)
    sess.commit()
    return asset
