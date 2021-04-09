from enum import Enum

import sqlalchemy as sa
from fastapi import APIRouter, Depends

from ._classes import NoExtraModel
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


class Asset(NoExtraModel):
    id: int
    name: str
    description: str
    is_active: bool
    type: str


@router.get("/")
def get_all(session: sa.orm.Session = Depends(get_session)):
    assets = session.query(models.Asset).all()
    return assets
