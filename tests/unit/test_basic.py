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


def test_db_starts_with_no_accounts(session):
    accs = traded.crud.get_accounts(session)
    assert len(accs) == 0


def test_create_root_account(session):
    # insert
    acc_obj = traded.schemas.AccountCreate(
        name="root",
        postable=True,
    )
    acc = traded.crud.insert_account(session, acc_obj)

    # check
    accs = traded.crud.get_accounts(session)
    assert len(accs) == 1
    assert accs[0] == acc
