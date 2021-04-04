import datetime as dt
from decimal import Decimal

import pytest

import traded


@pytest.fixture(scope="function")
def sess():
    engine = traded.database.create_engine(traded.database.DATABASE_URL)
    SessionLocal = traded.database.sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
    session = SessionLocal()
    traded.database.Base.metadata.create_all(bind=engine)
    traded.account.create_default_coa(session)
    traded.asset.create_default_assets(session)

    try:
        yield session
    finally:
        session.close()


def test_should_always_pass():
    pass


def test_insert_manual_transaction(sess):
    "Inserts a forex transaction"

    acc_cash = traded.account.get_by_name(sess, "Cash")
    acc_fee = traded.account.get_by_name(sess, "Broker")
    asset_usd = traded.asset.get_by_name(sess, "USD")
    asset_brl = traded.asset.get_by_name(sess, "BRL")

    # sell brl
    entry1 = traded.transaction.EntryCreate(
        datetime=dt.datetime(2021, 1, 1, 13, 0, 0),
        account=acc_cash,
        value=Decimal("-1234.58"),
        asset_id=asset_brl.id,
        qnt=Decimal("-1234.58"),
    )
    # buy usd
    entry2 = traded.transaction.EntryCreate(
        datetime=dt.datetime(2021, 1, 1, 13, 0, 0),
        account=acc_cash,
        value=Decimal("1234"),
        asset_id=asset_usd.id,
        qnt=Decimal("200"),
    )
    # fees
    entry3 = traded.transaction.EntryCreate(
        datetime=dt.datetime(2021, 1, 1, 13, 0, 0),
        account=acc_fee,
        value=Decimal("0.58"),
        asset_id=asset_usd.id,
        qnt=Decimal("1"),
    )

    transaction = traded.transaction.TransactionCreate(
        entries=[entry1, entry2, entry3],
        description="unit testing",
        datetime=dt.datetime(2021, 4, 3, 21, 0, 0),
    )
    transaction = traded.transaction.insert(sess, transaction)
    assert transaction.id == 1
    assert len(transaction.entries) == 3
    assert transaction.entries[0].value == Decimal("-1234.58")
