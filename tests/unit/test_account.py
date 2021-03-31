import pytest

import traded


@pytest.fixture(scope="function")
def session():
    engine = traded.database.create_engine(traded.database.DATABASE_URL)
    SessionLocal = traded.database.sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
    session = SessionLocal()
    traded.database.Base.metadata.create_all(bind=engine)

    try:
        yield session
    finally:
        session.close()


def test_should_always_pass():
    pass


def test_db_starts_with_no_accounts(session):
    accs = traded.account.get(session)
    assert len(accs) == 0


def test_create_root(session):
    test_db_starts_with_no_accounts(session)

    # insert
    acc_obj = traded.account.AccountCreate(
        name="root",
        postable=False,
    )
    acc = traded.account.insert(session, acc_obj)

    # check
    accs = traded.account.get(session)
    assert len(accs) == 1
    assert accs[0] == acc
    return acc
