import contextlib
import json
import logging
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

from . import config, models

logger = logging.getLogger(__name__)


def _default(val):
    if isinstance(val, Decimal):
        return str(val)
    raise TypeError()


def _dumps(d):
    return json.dumps(d, default=_default)


@contextlib.contextmanager
def create_session():
    """
    Yield a session through context manager.

    To be used inside `with` blocks.
    """

    if config.settings.sqlite:
        logger.debug("Initializing sqlite database")
        url = "sqlite://"
        engine = sa.create_engine(
            url,
            connect_args={"check_same_thread": False},
            poolclass=sa.pool.StaticPool,
            json_serializer=_dumps,
        )
    else:
        logger.debug("Initializing postgres database")
        url = URL.create(
            drivername="postgresql",
            username=config.settings.db.user,
            password=config.settings.db.password.get_secret_value(),
            host=config.settings.db.host,
            database=config.settings.db.name,
        )
        engine = sa.create_engine(
            url,
            json_serializer=_dumps,
            pool_size=config.settings.db.pool_size,
            max_overflow=10,
            pool_timeout=5,
        )

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    if config.settings.sqlite:
        session = SessionLocal()
        models.Base.metadata.create_all(bind=engine)
        session.close()

    # session_factory = SessionLocal()
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
