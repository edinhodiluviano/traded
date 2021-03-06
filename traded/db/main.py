import os as _os
import traceback as tb

import sqlalchemy as sa
from fastapi import HTTPException

from . import models, _insert_defaults


DATABASE_URL = _os.environ["DATABASE_URL"]


engine = sa.create_engine(DATABASE_URL)
SessionLocal = sa.orm.sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


def setup(session: sa.orm.Session):
    "Create tables and insert basic entries"
    create_tables()
    populate(session)


def create_tables():
    "Create tables"
    models.Base.metadata.create_all(bind=engine)


def populate(session: sa.orm.Session):
    "Insert basic entries"
    _insert_defaults.all(session)


def clear(session: sa.orm.Session):
    "Just delete entries for all tables"
    for table in models.Base.metadata.tables.values():
        session.query(table).delete()
    session.commit()


def reset(session: sa.orm.Session):
    "Delete entries for all tables insert basic entries"
    clear(session)
    populate(session)


def try_to_commit(session: sa.orm.Session):
    try:
        session.commit()
    except sa.exc.IntegrityError:
        session.rollback()
        raise HTTPException(status_code=422, detail=tb.format_exc(limit=0))
