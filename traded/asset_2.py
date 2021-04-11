from enum import Enum
import traceback as tb

import sqlalchemy as sa
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Path, HTTPException

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

    class Config:
        extra = "forbid"
        orm_mode = True


class Asset(_AssetBase):
    id: int
    type: AssetTypes


class CurrencyCreate(_AssetBase):
    pass


class Currency(_AssetBase):
    id: int


class StockCreate(_AssetBase):
    pass


class Stock(_AssetBase):
    id: int


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


def create_asset_factory(
    asset_type: AssetTypes,
    asset_create_class: _AssetBase,
):
    def create_asset(
        asset_create: asset_create_class,
        session: sa.orm.Session = Depends(get_session),
    ):
        asset_dict = asset_create.dict()
        asset_dict["type"] = asset_type.value
        asset_db = models.Asset(**asset_dict)
        session.add(asset_db)
        try:
            session.commit()
        except sa.exc.IntegrityError:
            session.rollback()
            raise HTTPException(status_code=422, detail=tb.format_exc(limit=0))
        else:
            session.refresh(asset_db)
            return asset_db

    create_asset.__name__ = f"Create {asset_type.value.title()}"
    create_asset.__doc__ = (
        f"Creates an asset of type {asset_type.value.title()}"
    )
    return create_asset


def update_asset_factory(
    asset_type: AssetTypes,
    asset_create_class: _AssetBase,
):
    def update_asset(
        asset_id: int,
        asset_update: asset_create_class,
        session: sa.orm.Session = Depends(get_session),
    ):
        asset_db = session.query(models.Asset).get(asset_id)
        for field, value in asset_update.dict().items():
            setattr(asset_db, field, value)
        try:
            session.commit()
        except sa.exc.IntegrityError:
            session.rollback()
            raise HTTPException(status_code=422, detail=tb.format_exc(limit=0))
        else:
            session.refresh(asset_db)
            return asset_db

    update_asset.__name__ = f"Update {asset_type.value.title()}"
    update_asset.__doc__ = f"Updates a single {asset_type.value.title()}"

    return update_asset


def endpoints_factory(
    asset_type: AssetTypes,
    asset_create_class: _AssetBase,
    response_model: _AssetBase,
):

    # create endpoint
    endpoint = f"/{asset_type.value}"
    create_func = create_asset_factory(
        asset_type=asset_type,
        asset_create_class=asset_create_class,
    )
    router.post(endpoint, response_model=response_model)(create_func)

    # update endpoint
    endpoint = f"/{asset_type.value}/{{asset_id}}"
    update_func = update_asset_factory(
        asset_type=asset_type,
        asset_create_class=asset_create_class,
    )
    router.put(endpoint, response_model=response_model)(update_func)


endpoints_factory(AssetTypes.currency, CurrencyCreate, Currency)
endpoints_factory(AssetTypes.stock, CurrencyCreate, Currency)
