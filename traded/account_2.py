import sqlalchemy as sa
from fastapi import APIRouter, Depends

from ._classes import NoExtraModel
from .dependencies import get_session
from .db import models


router = APIRouter(
    prefix="/account",
    tags=["account"],
)


class Account(NoExtraModel):
    id: int
    name: str
    postable: bool
    is_active: bool


@router.get("/")
def get_by_name(name: str, session: sa.orm.Session = Depends(get_session)):
    acc = (
        session.query(models.Account)
        .filter(models.Account.name == name)
        .first()
    )
    return acc
