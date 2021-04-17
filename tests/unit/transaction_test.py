import datetime as dt

import pytest


@pytest.fixture(scope="module")
def fund_id(client):
    name = "aaa"
    fund = dict(name=name, temporary=True, asset_id=1)
    resp = client.post("/fund", json=fund)
    yield resp.json()["id"]


def test_insert_transaction(client, fund_id):
    entry1 = dict(
        account_id=1,
        value=10,
        asset_id=2,
        quantity=10,
    )
    entry2 = dict(
        account_id=2,
        value=-10,
        asset_id=2,
        quantity=-10,
    )
    transaction = dict(
        datetime=dt.datetime(2021, 4, 12, 16).isoformat(timespec="seconds"),
        description="testing transaction",
        entries=[entry1, entry2],
        fund_id=fund_id,
    )
    resp = client.post("/transaction", json=transaction)
    assert resp.status_code == 200
    t = resp.json()
    check_is_a_valid_transaction(t)
    entries = t["entries"]
    assert isinstance(entries, list)
    assert len(entries) == 2
    assert t["value"] == 10
    assert entries[0]["value"] == 10
    assert entries[1]["value"] == -10


def check_is_a_valid_transaction(transaction):
    assert isinstance(transaction, dict)
    for field in ["id", "timestamp", "datetime", "entries", "value", "cancel"]:
        assert field in transaction
    assert isinstance(transaction["id"], int)
    _ = dt.datetime.fromisoformat(transaction["datetime"])
    _ = dt.datetime.fromisoformat(transaction["timestamp"])
    assert isinstance(transaction["value"], float)
    assert transaction["value"] > 0
    entries = transaction["entries"]
    assert isinstance(entries, list)
    assert len(entries) >= 2
    for entry in entries:
        assert entry["value"] != 0


def test_get_transactions(client, fund_id):
    test_insert_transaction(client, fund_id)
    resp = client.get("/transaction")
    assert resp.status_code == 200
    transactions = resp.json()
    for transaction in transactions:
        check_is_a_valid_transaction(transaction)


def test_revert_transaction(client, fund_id):
    # create initial transactions
    test_insert_transaction(client, fund_id)
    resp = client.get("/transaction")
    transactions1 = resp.json()
    # revert
    resp2 = client.delete(f"/transaction/{transactions1[0]['id']}")
    assert resp2.status_code == 200
    transaction = resp2.json()
    check_is_a_valid_transaction(transaction)
    assert transaction["cancel"]
    assert transaction["value"] == transactions1[0]["value"]
    assert len(transaction["entries"]) == len(transactions1[0]["entries"])
    for n in range(len(transaction["entries"])):
        assert (
            transaction["entries"][n]["value"]
            == -transactions1[0]["entries"][n]["value"]
        )
    # check a new transaction was registered
    resp3 = client.get("/transaction")
    transactions2 = resp3.json()
    assert len(transactions2) == len(transactions1) + 1


def test_insert_transaction_with_0_entry_value(client, fund_id):
    entry1 = dict(
        account_id=1,
        value=0,
        asset_id=2,
        quantity=10,
    )
    entry2 = dict(
        account_id=2,
        value=-10,
        asset_id=2,
        quantity=-10,
    )
    entry3 = dict(
        account_id=3,
        value=10,
        asset_id=2,
        quantity=10,
    )
    transaction = dict(
        datetime=dt.datetime(2021, 4, 12, 16).isoformat(timespec="seconds"),
        description="testing transaction",
        entries=[entry1, entry2, entry3],
        fund_id=fund_id,
    )
    resp = client.post("/transaction", json=transaction)
    assert resp.status_code == 422


def test_insert_transaction_with_0_entry_quantity(client, fund_id):
    entry1 = dict(
        account_id=1,
        value=10,
        asset_id=2,
        quantity=0,
    )
    entry2 = dict(
        account_id=2,
        value=-10,
        asset_id=2,
        quantity=-10,
    )
    transaction = dict(
        datetime=dt.datetime(2021, 4, 12, 16).isoformat(timespec="seconds"),
        description="testing transaction",
        entries=[entry1, entry2],
        fund_id=fund_id,
    )
    resp = client.post("/transaction", json=transaction)
    assert resp.status_code == 422


def test_insert_transaction_with_imbalanced_entries(client, fund_id):
    entry1 = dict(
        account_id=1,
        value=11,
        asset_id=2,
        quantity=10,
    )
    entry2 = dict(
        account_id=2,
        value=-10,
        asset_id=2,
        quantity=-10,
    )
    transaction = dict(
        datetime=dt.datetime(2021, 4, 12, 16).isoformat(timespec="seconds"),
        description="testing transaction",
        entries=[entry1, entry2],
        fund_id=fund_id,
    )
    resp = client.post("/transaction", json=transaction)
    assert resp.status_code == 422


def test_insert_transaction_with_no_entries(client, fund_id):
    transaction = dict(
        datetime=dt.datetime(2021, 4, 12, 16).isoformat(timespec="seconds"),
        description="testing transaction",
        entries=[],
        fund_id=fund_id,
    )
    resp = client.post("/transaction", json=transaction)
    assert resp.status_code == 422


def test_cancel_non_existing_transaction(client):
    resp = client.delete("/transaction/999999")
    assert resp.status_code == 404
