import datetime as dt


def test_insert_transaction(client):
    resp1 = client.get("/asset")
    asset = resp1.json()[0]
    account1 = client.get("/account", params=dict(name="Cash")).json()
    account2 = client.get("/account", params=dict(name="Receivables")).json()

    entry1 = dict(
        account_id=account1["id"],
        value=10,
        asset_id=asset["id"],
        quantity=10,
    )
    entry2 = dict(
        account_id=account2["id"],
        value=-10,
        asset_id=asset["id"],
        quantity=-10,
    )
    transaction = dict(
        datetime=dt.datetime(2021, 4, 12, 16).isoformat(timespec="seconds"),
        description="testing transaction",
        entries=[entry1, entry2],
    )
    resp = client.post("/transaction", json=transaction)
    print(resp.json())
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
    for field in ["id", "timestamp", "datetime", "entries", "value"]:
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


def test_get_transactions(client):
    test_insert_transaction(client)
    resp = client.get("/transaction")
    assert resp.status_code == 200
    transactions = resp.json()
    for transaction in transactions:
        check_is_a_valid_transaction(transaction)


def test_revert_transaction(client):
    pass
