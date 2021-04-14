import sqlalchemy as sa
from fastapi import APIRouter

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
    postable: bool
    is_active: bool


@router.get("/")
def get_by_name(name: str, session: sa.orm.Session = sess):
    acc = (
        session.query(models.Account)
        .filter(models.Account.name == name)
        .first()
    )
    return acc
