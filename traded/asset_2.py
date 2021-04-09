from enum import Enum
import datetime as dt
from decimal import Decimal

import sqlalchemy as sa
from fastapi import APIRouter, Depends
from pydantic import BaseModel

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
    type: AssetTypes


class Asset(_AssetBase):
    id: int

    class Config:
        orm_mode = True


@router.get("/", response_model=list[Asset])
def get_all(session: sa.orm.Session = Depends(get_session)):
    assets = session.query(models.Asset).all()
    return assets
