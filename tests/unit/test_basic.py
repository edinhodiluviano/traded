import pytest

import traded


def test_should_always_pass():
    pass


@pytest.fixture(scope="function")
def session():
    session = traded.database.SessionLocal()
    traded.database.create_tables()
    try:
        yield session
    finally:
        session.close()
