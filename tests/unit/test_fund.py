import pytest


@pytest.fixture(scope="module")
def resp(client):
    name = "aaa"
    resp = client.post("/fund", json=dict(name=name, temporary=False))
    yield resp


def check_valid_fund(fund):
    assert isinstance(fund["name"], str)
    assert isinstance(fund["id"], int)
    assert fund["temporary"] in {True, False}


def test_insert_fund(resp):
    assert resp.status_code == 200
    fund = resp.json()
    check_valid_fund(fund)
    assert fund["name"] == "aaa"
    assert fund["id"] == 1
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
    resp1 = client.post("/fund", json=dict(name=name, temporary=True))
    fund = resp1.json()
    resp2 = client.delete(f"/fund/{fund['id']}")
    assert resp2.status_code == 200
    assert resp2.json() is None
    resp3 = client.get("/fund")
    assert len(resp3.json()) == 1
