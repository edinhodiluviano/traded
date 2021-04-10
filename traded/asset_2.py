from enum import Enum

import sqlalchemy as sa
from fastapi import APIRouter, Depends, Path
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


class CurrencyCreate(_AssetBase):
    type: AssetTypes = AssetTypes.currency

    class Config:
        extra = "forbid"


class Currency(CurrencyCreate):
    id: int

    class Config:
        orm_mode = True


@router.get("/a", response_model=list[Asset])
def get_all(session: sa.orm.Session = Depends(get_session)):
    assets = session.query(models.Asset).all()
    return assets


@router.get("/a/{asset_id}", response_model=Asset)
def get_by_id(
    asset_id: int = Path(..., ge=1),
    session: sa.orm.Session = Depends(get_session),
):
    query = session.query(models.Asset)
    asset = query.filter(models.Asset.id == asset_id).first()
    return asset


@router.post("/currency", response_model=Currency)
def create_currency(
    currency: CurrencyCreate,
    session: sa.orm.Session = Depends(get_session),
):
    currency_db = models.Asset(**currency.dict())
    session.add(currency_db)
    session.commit()
    session.refresh(currency_db)
    return currency_db


@router.get("/currency", response_model=list[Currency])
def get_all_currencies(session: sa.orm.Session = Depends(get_session)):
    query = session.query(models.Asset)
    currencies = query.filter(models.Asset.type == AssetTypes.currency).all()
    return currencies


@router.put("/currency/{asset_id}", response_model=Currency)
def update_currency(
    currency: CurrencyCreate,
    asset_id: int = Path(..., ge=1),
    session: sa.orm.Session = Depends(get_session),
):
    asset = session.query(models.Asset).get(asset_id)
    for field, value in currency.dict().items():
        if field == "id":
            continue
        setattr(asset, field, value)
    session.commit()
    session.refresh(asset)
    return asset
