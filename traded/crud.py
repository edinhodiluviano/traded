from sqlalchemy.orm import Session

from . import models, schemas


def get_account_by_id(db: Session, account_id: int):
    query = db.query(models.Account).filter(models.Account.id == account_id)
    return query.first()


def get_accounts(db: Session, offset: int = 0, limit: int = 0):
    query = db.query(models.Account)
    if offset > 0:
        query = query.offset(offset)
    if limit > 0:
        query = query.limit(limit)
    return query.all()


def insert_account(db: Session, account: schemas.Account):
    db_acc = models.Account(**account.dict())
    db.add(db_acc)
    db.commit()
    db.refresh(db_acc)
    return db_acc
