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
    option = "option"
    future = "future"
    index = "index"
    bond = "bond"
    rate = "rate"


class RateFrequencies(str, Enum):
    daily = "daily"
    monthly = "monthly"


class DayCountConvention(str, Enum):
    d30_360 = "30/360"
    actual_actual = "Actual/Actual"
    actual_360 = "Actual/360"
    d252 = "252"


class _AssetBase(BaseModel):
    name: str
    description: str
    is_active: bool
    type: str

    opt_expiration: dt.datetime = None
    opt_strike: Decimal = None
    opt_underlying_id: int = None

    fut_expiration: dt.datetime = None
    fut_underlying_id: int = None

    # bond
    bond_expiration: dt.datetime = None
    bond_value: Decimal = None

    # rate
    rate_frequency: RateFrequencies = None
    rate_day_count: DayCountConvention = None


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
