from enum import Enum
import datetime as dt
from decimal import Decimal

import sqlalchemy as sa
from fastapi import APIRouter, Depends

from ._classes import BaseModel, NoExtraModel
from .dependencies import get_session
from .db import models


router = APIRouter(
    prefix="/asset",
    tags=["asset"],
)


class AssetTypes(str, Enum):
    currency = "currency"
    stock = "stock"
    fund = "fund"
    bond = "bond"


class _AssetBase(BaseModel):
    name: str
    description: str
    is_active: bool
    type: str

    # bond
    bond_expiration: dt.datetime = None
    bond_value: Decimal = None


class AssetCreate(_AssetBase):
    pass


class Asset(_AssetBase, NoExtraModel):
    id: int
    opt_underlying: "Asset" = None
    fut_underlying: "Asset" = None


Asset.update_forward_refs()


@router.get("/")
def get_all(session: sa.orm.Session = Depends(get_session)):
    assets = session.query(models.Asset).all()
    return assets
