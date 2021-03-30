import os

import pytest

import traded


def test_should_always_pass():
    pass


@pytest.fixture(scope="function")
def db():
    os.environ["DATABASE_URL"] = "sqlite://"
    db = traded.database.SessionLocal()
    traded.database.create_tables()
    try:
        yield db
    finally:
        db.close()


def test_db_starts_with_no_accoutns(db):
    accs = traded.crud.get_accounts(db)
    assert len(accs) == 0


def test_create_root_account(db):
    # insert
    acc_obj = traded.schemas.AccountCreate(
        name="root",
        postable=True,
    )
    acc = traded.crud.insert_account(db, acc_obj)

    # check
    accs = traded.crud.get_accounts(db)
    assert len(accs) == 1
    assert accs[0] == acc
