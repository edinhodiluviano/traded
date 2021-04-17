import datetime as dt

import pytest


@pytest.fixture(scope="module")
def resp(client):
    name = "aaa"
    fund = dict(name=name, temporary=False, asset_id=1)
    resp = client.post("/fund", json=fund)
    print(resp.json())
    yield resp


def check_valid_fund(fund):
    for field in ["name", "id", "asset", "temporary"]:
        assert field in fund
    assert isinstance(fund["name"], str)
    assert isinstance(fund["id"], int)
    assert isinstance(fund["asset"], dict)
    assert fund["temporary"] in {True, False}


def test_insert_fund(resp):
    assert resp.status_code == 200
    fund = resp.json()
    check_valid_fund(fund)
    assert fund["name"] == "aaa"
    assert fund["id"] >= 1
    assert not fund["temporary"]


def test_get_all(resp, client):
    resp2 = client.get("/fund")
    assert isinstance(resp2.json(), list)
    assert len(resp2.json()) == 1


def test_get_by_id(resp, client):
    resp2 = client.get("/fund/1")
    assert isinstance(resp2.json(), dict)
    check_valid_fund(resp2.json())
    assert resp2.json()["id"] == 1
    assert resp2.json()["name"] == "aaa"


def test_delete_fund_with_inexistent_fund(resp, client):
    resp2 = client.delete("/fund/99999999999")
    assert resp2.status_code == 404


def test_delete_fund_not_temporary(resp, client):
    resp2 = client.delete(f"/fund/{resp.json()['id']}")
    assert resp2.status_code == 403


def test_delete_fund(client):
    name = "bbb"
    fund_dict = dict(name=name, temporary=True, asset_id=1)
    resp1 = client.post("/fund", json=fund_dict)
    fund = resp1.json()
    resp2 = client.delete(f"/fund/{fund['id']}")
    assert resp2.status_code == 200
    assert resp2.json() is None
    resp3 = client.get("/fund")
    assert len(resp3.json()) == 1


def test_delete_fund_also_delete_its_transactions(client):
    # insert fund
    name = "bbb"
    fund_dict = dict(name=name, temporary=True, asset_id=1)
    resp1 = client.post("/fund", json=fund_dict)
    fund_id = resp1.json()["id"]

    # insert transaction
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
    transaction = resp.json()

    # delete fund
    resp2 = client.delete(f"/fund/{fund_id}")
    print(resp2.json())
    assert resp2.status_code == 200

    # check fund is gone
    resp3 = client.get("f/fund/{fund_id}")
    assert resp3.status_code == 404

    # check transaction is gone
    resp4 = client.get("/transaction")
    for check_trans in resp4.json():
        print("=" * 30)
        print(f"{fund_id=}")
        print(f"{check_trans=}")
        assert check_trans["fund_id"] != fund_id
        assert check_trans["id"] != transaction["id"]


def test_create_fund_with_non_existent_asset(client):
    name = "ccc"
    fund_dict = dict(name=name, temporary=True, asset_id=9999999)
    resp = client.post("/fund", json=fund_dict)
    assert resp.status_code == 422
