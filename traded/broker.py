import sqlalchemy as sa
from fastapi import APIRouter, Path

from ._classes import NoExtraModel
from .dependencies import sess
from . import db


router = APIRouter(
    prefix="/broker",
    tags=["broker"],
)


class BrokerCreate(NoExtraModel):
    name: str


class Broker(BrokerCreate):
    id: int


@router.get("", response_model=list[Broker])
def get_all(session: sa.orm.Session = sess):
    query = session.query(db.models.Broker)
    brokers = query.all()
    return brokers


@router.get("/{broker_id}", response_model=Broker)
def get_by_id(
    broker_id: int = Path(..., ge=1),
    session: sa.orm.Session = sess,
):
    query = session.query(db.models.Broker)
    broker = query.filter(db.models.Broker.id == broker_id).first()
    return broker


@router.put("/{broker_id}", response_model=Broker)
def update_broker(
    broker_update: BrokerCreate,
    broker_id: int = Path(..., ge=1),
    session: sa.orm.Session = sess,
):
    broker_db = session.query(db.models.Broker).get(broker_id)
    for field, value in broker_update.dict().items():
        setattr(broker_db, field, value)
    db.main.try_to_commit(session)
    session.refresh(broker_db)
    return broker_db


@router.post("", response_model=Broker)
def create_broker(
    broker: BrokerCreate,
    session: sa.orm.Session = sess,
):
    """
    Creates a new broker

    Parameters:
    name: str
        The broker name
    """

    broker_db = db.models.Broker(**broker.dict())
    session.add(broker_db)
    db.main.try_to_commit(session)
    session.refresh(broker_db)
    return broker_db
