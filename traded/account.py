import sqlalchemy as sa
from fastapi import APIRouter, HTTPException

from ._classes import NoExtraModel
from .dependencies import sess
from .db import models


router = APIRouter(
    prefix="/account",
    tags=["account"],
)


class Account(NoExtraModel):
    id: int
    name: str


@router.get("/")
def get_by_name(name: str, session: sa.orm.Session = sess):
    acc = (
        session.query(models.Account)
        .filter(models.Account.name == name)
        .first()
    )
    if acc is None:
        msg = f"Account {name} doesn't exists"
        raise HTTPException(status_code=404, detail=msg)
    return acc
