import datetime as dt

import pytest


@pytest.fixture(scope="module", autouse=True)
def insert_sample_transactions(client):
    # create fund
    fund = dict(name="fund", temporary=False, asset_id=1)
    resp = client.post("/fund", json=fund)
    assert resp.status_code == 200
    fund_id = resp.json()["id"]

    # issuing shares
    entry1 = dict(
        account_id=8,
        value=-1000,
        asset_id=fund_id,
        quantity=-10,
    )
    entry2 = dict(
        account_id=3,
        value=1000,
        asset_id=3,
        quantity=1000,
    )
    transaction = dict(
        datetime=dt.datetime(2021, 1, 1, 0, 0).isoformat(timespec="seconds"),
        description="Initial share offering",
        entries=[entry1, entry2],
        fund_id=fund_id,
    )
    resp2 = client.post("/transaction", json=transaction)
    assert resp2.status_code == 200

    # make an fx with a future delivery date
    entry1 = dict(  # sell 500 usd
        account_id=3,
        value=-500,
        asset_id=1,
        quantity=-500,
    )
    entry2 = dict(  # buy 400 eur (with a value of 500 usd)
        account_id=4,
        value=500,
        asset_id=2,
        quantity=400,
    )
    transaction = dict(
        datetime=dt.datetime(2021, 1, 2, 0, 0).isoformat(timespec="seconds"),
        description="USD/EUR fx",
        entries=[entry1, entry2],
        fund_id=fund_id,
    )
    resp2 = client.post("/transaction", json=transaction)
    assert resp2.status_code == 200


def test_fixture_insert_sample_transactions(client):
    pass


def test_get_balance_sheet(client):
    resp = client.get(
        "/finance/balancesheet/1",
        params={"datetime": "2021-01-02T00:00:00"},
    )
    assert resp.status_code == 200
    bs = resp.json()
    assert isinstance(bs, dict)
    assert bs["name"] == "root"
    assert bs["balance"] == 0
    assert bs["childs"][0]["childs"][0]["balance"] == 500


def _get_account_from_tree(tree: dict, account_id: int) -> dict:
    if tree["id"] == account_id:
        return tree
    for child in tree["childs"]:
        acc = _get_account_from_tree(child, account_id)
        if acc.id == account_id:
            return acc
