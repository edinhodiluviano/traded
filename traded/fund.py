import sqlalchemy as sa
from fastapi import APIRouter, Path, HTTPException

from ._classes import NoExtraModel
from .dependencies import sess
from . import db


router = APIRouter(
    prefix="/fund",
    tags=["fund"],
)


class FundCreate(NoExtraModel):
    name: str
    temporary: bool


class Fund(FundCreate):
    id: int


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


@router.post("", response_model=Fund)
def create_fund(
    fund: FundCreate,
    session: sa.orm.Session = sess,
):
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
