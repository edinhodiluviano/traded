from enum import Enum
import traceback as tb

import sqlalchemy as sa
from fastapi import APIRouter, Depends, Path, HTTPException
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
def get_all_assets(session: sa.orm.Session = Depends(get_session)):
    query = session.query(models.Asset)
    assets = query.all()
    return assets


@router.get("/{asset_id}", response_model=Asset)
def get_by_id(
    asset_id: int = Path(..., ge=1),
    session: sa.orm.Session = Depends(get_session),
):
    query = session.query(models.Asset)
    asset = query.filter(models.Asset.id == asset_id).first()
    return asset


class CurrencyCreate(_AssetBase):
    type: AssetTypes = AssetTypes.currency

    class Config:
        extra = "forbid"


class Currency(CurrencyCreate):
    id: int

    class Config:
        orm_mode = True


class StockCreate(_AssetBase):
    type: AssetTypes = AssetTypes.stock

    class Config:
        extra = "forbid"


class Stock(StockCreate):
    id: int

    class Config:
        orm_mode = True


@router.post("/currency", response_model=Currency)
def create_currency(
    currency: CurrencyCreate,
    session: sa.orm.Session = Depends(get_session),
):
    currency_db = models.Asset(**currency.dict())
    session.add(currency_db)
    try:
        session.commit()
    except sa.exc.IntegrityError:
        session.rollback()
        raise HTTPException(status_code=422, detail=tb.format_exc(limit=0))
    else:
        session.refresh(currency_db)
        return currency_db


@router.post("/stock", response_model=Stock)
def create_stock(
    stock: StockCreate,
    session: sa.orm.Session = Depends(get_session),
):
    stock_db = models.Asset(**stock.dict())
    session.add(stock_db)
    session.commit()
    session.refresh(stock_db)
    return stock_db


@router.put("/currency/{asset_id}", response_model=Currency)
def update_currency(
    currency: CurrencyCreate,
    asset_id: int = Path(..., ge=1),
    session: sa.orm.Session = Depends(get_session),
):
    asset = session.query(models.Asset).get(asset_id)
    for field, value in currency.dict().items():
        setattr(asset, field, value)
    session.commit()
    session.refresh(asset)
    return asset


@router.put("/stock/{asset_id}", response_model=Stock)
def update_stock(
    stock: StockCreate,
    asset_id: int = Path(..., ge=1),
    session: sa.orm.Session = Depends(get_session),
):
    asset = session.query(models.Asset).get(asset_id)
    for field, value in stock.dict().items():
        setattr(asset, field, value)
    session.commit()
    session.refresh(asset)
    return asset
