"""
A module to access the database and quickly create session.

The public objects available are create_session and Session.

Example of usage:
```
with database.create_session() as session:
    results = session.dql('select * from table;')
print(results)
>>> [{'id': 1, 'column': 'a'}, {'id': 2, 'column': 'b'}]
```
"""

import contextlib
import functools
import logging
from collections.abc import Callable, Iterator
from textwrap import dedent
from typing import Any, TypeAlias

import sqlalchemy as sa
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.orm import Session as SqlaSession


logger = logging.getLogger(__name__)


DictRecord: TypeAlias = dict[str, Any]


class Database(BaseSettings):
    """Dataclass that loads the database information."""

    model_config = SettingsConfigDict(frozen=True, env_prefix='DATABASE_')
    filename: str


def _create_url(db: Database) -> sa.engine.URL:
    url = sa.engine.URL.create(
        drivername='sqlite',
        database=db.filename,
    )
    return url


@functools.cache
def _create_engine(
    db: Database,
    create_url: Callable[[Database], sa.engine.URL],
) -> sa.engine.Engine:
    url = create_url(db)
    logger.debug(f'Creating connection engine for {db=}')
    engine = sa.create_engine(
        url,
        pool_size=1,
        max_overflow=1,
        pool_timeout=5,
    )
    logger.debug('Connection engine created')
    return engine


class Session(SqlaSession):
    """A standard SqlAlchemy Session class with two custom methods."""

    def dql(
        self,
        query: str | sa.sql.elements.TextClause,
        params: dict[str, Any] | None = None,
    ) -> list[DictRecord]:
        """Execute a dql statement (select) and returns a list of dict."""
        query = sa.text(query) if isinstance(query, str) else query
        logger.info('Executing:\n' + dedent(str(query)))
        params = {} if params is None else params
        cursor = self.execute(query, params=params)
        column_names = list(cursor.keys())
        rows_as_tuples = cursor.fetchall()
        rows_as_dict = [
            dict(zip(column_names, row, strict=False))
            for row in rows_as_tuples
        ]
        return rows_as_dict

    def dml(self, query: str | sa.sql.elements.TextClause) -> None:
        """Execute a dml statement (insert, update) and returns None."""
        query = sa.text(query) if isinstance(query, str) else query
        logger.info('Executing:\n' + dedent(str(query)))
        self.execute(query)

    def commit(self) -> None:
        """Log and call the common Sqlalchemy Session commit."""
        logger.info('Preparing to commit transaction')
        super().commit()
        logger.info('Finished commit')


@contextlib.contextmanager
def create_session(
    creds: Database | None = None,
    create_url: Callable[[Database], sa.engine.URL] = _create_url,
) -> Iterator[Session]:
    """Return a SQLAlchemy Session through a context manager."""
    curr_creds = Database() if creds is None else creds
    engine = _create_engine(db=curr_creds, create_url=create_url)
    session_local = sa.orm.sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        class_=Session,
    )
    sess = session_local()

    try:
        yield sess
    finally:
        sess.close()
