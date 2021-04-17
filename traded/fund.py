import sqlalchemy as sa
from fastapi import APIRouter, Path, HTTPException

from ._classes import NoExtraModel
from .asset import AssetTypes, Currency
from .dependencies import sess
from . import db


router = APIRouter(
    prefix="/fund",
    tags=["fund"],
)


class FundCreate(NoExtraModel):
    name: str
    temporary: bool
    asset_id: int


class Fund(NoExtraModel):
    id: int
    name: str
    temporary: bool
    asset: Currency


@router.get("", response_model=list[Fund])
def get_all(session: sa.orm.Session = sess):
    query = session.query(db.models.Fund)
    assets = query.all()
    return assets


@router.get("/{fund_id}", response_model=Fund)
def get_by_id(
    fund_id: int = Path(..., ge=1),
    session: sa.orm.Session = sess,
):
    query = session.query(db.models.Fund)
    fund = query.filter(db.models.Fund.id == fund_id).first()
    return fund


def _asset_is_currency(asset_id: int, session: sa.orm.Session):
    asset = session.query(db.models.Asset).get(asset_id)
    if asset is None:
        return False
    return asset.type == AssetTypes.currency


@router.post("", response_model=Fund)
def create_fund(
    fund: FundCreate,
    session: sa.orm.Session = sess,
):
    """
    Creates a new fund

    Parameters:
    name: str
        The fund name

    temporary: bool
        Whether the fund is temporary or not
        Temporary funds can be deleted allong with all its transactions

    asset_id: int
        The identifier of the fund currency id
        It is used to mark-to-market the fund's assets
    """

    if not _asset_is_currency(fund.asset_id, session):
        msg = "Fund asset must be a currency"
        raise HTTPException(status_code=422, detail=msg)
    fund_db = db.models.Fund(**fund.dict())
    session.add(fund_db)
    db.main.try_to_commit(session)
    session.refresh(fund_db)
    return fund_db


@router.delete("/{fund_id}")
def delete_fund(
    fund_id: int = Path(..., ge=1),
    session: sa.orm.Session = sess,
):
    """
    Deletes a temporary fund
    Only temporary funds can be deleted, otherwise you will get an 403 error
    When a fund is deleted, all of its transactions and entries are deleted too
    """

    fund = session.query(db.models.Fund).get(fund_id)
    if fund is None:
        msg = f"Fund {fund_id=} not found"
        raise HTTPException(status_code=404, detail=msg)

    if not fund.temporary:
        msg = "Only temporary funds can be deleted"
        raise HTTPException(status_code=403, detail=msg)

    session.delete(fund)
    db.main.try_to_commit(session)
    return None
