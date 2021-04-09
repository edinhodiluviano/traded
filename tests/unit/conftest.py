import pytest
import sqlalchemy as sa
from fastapi.testclient import TestClient

import traded


@pytest.fixture(scope="module")
def client():
    engine = sa.create_engine(
        traded.db.main.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=sa.pool.StaticPool,
    )
    traded.db.main.engine = engine
    SessionLocal = sa.orm.sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
    traded.db.main.SessionLocal = SessionLocal

    session = traded.db.main.SessionLocal()
    traded.db.main.setup(session)
    session.close()
    client = TestClient(traded.main.app)
    yield client
