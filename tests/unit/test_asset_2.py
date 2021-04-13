import uuid
import copy
import datetime as dt


def test_asset_get_all(client):
    resp = client.get("/asset")
    assert resp.status_code == 200
    assets = resp.json()
    assert isinstance(assets, list)


def test_asset_default_database(client):
    resp = client.get("/asset")
    assert len(resp.json()) > 0


def test_returned_assets_have_basic_fields(client):
    resp = client.get("/asset")
    for asset in resp.json():
        assert isinstance(asset, dict)
        assert "name" in asset
        assert "id" in asset
        assert "type" in asset
        assert "is_active" in asset


def test_get_by_id(client):
    resp = client.get("/asset/1")
    assert resp.status_code == 200
    assert resp.json()["id"] == 1


def test_get_by_id_with_str_as_id(client):
    resp = client.get("/asset/xxxx")
    assert resp.status_code == 422


def test_get_by_id_with_negative_id(client):
    resp = client.get("/asset/-1")
    assert resp.status_code == 422


def test_get_by_id_with_non_existing_id(client):
    resp = client.get("/asset/9999999")
    assert resp.status_code == 200
    assert resp.json() is None


def test_create_new_currency(client):
    name = str(uuid.uuid4())
    new_currency = dict(
        name=name,
        description="lcamds",
        is_active=True,
    )
    resp = client.post("/asset/currency", json=new_currency)
    assert resp.status_code == 200
    assert "id" in resp.json()
    assert "name" in resp.json()
    assert resp.json()["name"] == name


def test_create_new_currency_with_missing_data(client):
    name = str(uuid.uuid4())
    new_currency = dict(
        name=name,
        is_active=True,
    )
    resp = client.post("/asset/currency", json=new_currency)
    assert resp.status_code == 422


def test_create_new_currency_with_dupe_name(client):
    name = str(uuid.uuid4())
    new_currency = dict(
        name=name,
        description="lcamds",
        is_active=True,
    )
    resp = client.post("/asset/currency", json=new_currency)
    assert resp.status_code == 200
    resp = client.post("/asset/currency", json=new_currency)
    assert resp.status_code == 422


def test_create_new_currency_with_extra_data(client):
    name = str(uuid.uuid4())
    new_currency = dict(
        name=name,
        description="lcamds",
        is_active=True,
        bogus_field_123="cksdmcs",
    )
    resp = client.post("/asset/currency", json=new_currency)
    assert resp.status_code == 422


def test_edit_currency(client):
    name = str(uuid.uuid4())
    new_curr = dict(name=name, description="", is_active=True)
    resp = client.post("/asset/currency", json=new_curr)
    new_curr = resp.json()
    edited_curr = copy.deepcopy(new_curr)
    edited_curr["description"] = "aaa"
    del edited_curr["id"]
    resp2 = client.put(f"asset/currency/{new_curr['id']}", json=edited_curr)
    assert resp2.status_code == 200
    assert isinstance(resp2.json(), dict)
    for field in ["id", "name"]:
        assert resp2.json()[field] == new_curr[field]
    assert resp2.json()["description"] == "aaa"


def create_new_stock(client):
    name = str(uuid.uuid4())
    new_currency = dict(
        name=name,
        description=name,
        is_active=True,
    )
    return name, client.post("/asset/stock", json=new_currency)


def test_create_new_stock(client):
    name, resp = create_new_stock(client)
    assert resp.status_code == 200
    assert "id" in resp.json()
    assert "name" in resp.json()
    assert resp.json()["name"] == name


def test_create_new_stock_with_missing_data(client):
    name = str(uuid.uuid4())
    new_currency = dict(
        name=name,
        is_active=True,
    )
    resp = client.post("/asset/stock", json=new_currency)
    assert resp.status_code == 422


def test_create_new_stock_with_extra_data(client):
    name = str(uuid.uuid4())
    new_currency = dict(
        name=name,
        description=name,
        is_active=True,
        bogus_field_123="cksdmcs",
    )
    resp = client.post("/asset/stock", json=new_currency)
    assert resp.status_code == 422


def test_edit_stocks(client):
    name = str(uuid.uuid4())
    new_asset = dict(name=name, description="", is_active=True)
    resp = client.post("/asset/stock", json=new_asset)
    new_asset = resp.json()
    edited_asset = copy.deepcopy(new_asset)
    edited_asset["description"] = "aaa"
    del edited_asset["id"]
    resp2 = client.put(f"asset/stock/{new_asset['id']}", json=edited_asset)
    assert resp2.status_code == 200
    assert isinstance(resp2.json(), dict)
    for field in ["id", "name"]:
        assert resp2.json()[field] == new_asset[field]
    assert resp2.json()["description"] == "aaa"


def create_new_fund(client):
    name = str(uuid.uuid4())
    new_currency = dict(
        name=name,
        description=name,
        is_active=True,
    )
    return name, client.post("/asset/fund", json=new_currency)


def test_create_new_fund(client):
    name, resp = create_new_fund(client)
    assert resp.status_code == 200
    assert "id" in resp.json()
    assert "name" in resp.json()
    assert resp.json()["name"] == name


def test_create_new_fund_with_missing_data(client):
    name = str(uuid.uuid4())
    new_currency = dict(
        name=name,
        is_active=True,
    )
    resp = client.post("/asset/fund", json=new_currency)
    assert resp.status_code == 422


def test_create_new_fund_with_extra_data(client):
    name = str(uuid.uuid4())
    new_currency = dict(
        name=name,
        description=name,
        is_active=True,
        bogus_field_123="cksdmcs",
    )
    resp = client.post("/asset/fund", json=new_currency)
    assert resp.status_code == 422


def test_edit_funds(client):
    name = str(uuid.uuid4())
    new_asset = dict(name=name, description="", is_active=True)
    resp = client.post("/asset/fund", json=new_asset)
    new_asset = resp.json()
    edited_asset = copy.deepcopy(new_asset)
    edited_asset["description"] = "aaa"
    del edited_asset["id"]
    resp2 = client.put(f"asset/fund/{new_asset['id']}", json=edited_asset)
    assert resp2.status_code == 200
    assert isinstance(resp2.json(), dict)
    for field in ["id", "name"]:
        assert resp2.json()[field] == new_asset[field]
    assert resp2.json()["description"] == "aaa"


"""





"""


def create_new_bond(client):
    name = str(uuid.uuid4())
    new_bond = dict(
        name=name,
        description=name,
        is_active=True,
        bond_expiration=dt.datetime(2021, 4, 5, 14, 34).isoformat(
            timespec="seconds"
        ),
        bond_value="12.123456",
    )
    return name, client.post("/asset/bond", json=new_bond)


def test_create_new_bond(client):
    name, resp = create_new_bond(client)
    assert resp.status_code == 200
    assert isinstance(resp.json(), dict)
    fields = [
        "id",
        "name",
        "description",
        "is_active",
        "bond_expiration",
        "bond_value",
    ]
    for field in fields:
        assert field in resp.json()
    assert resp.json()["name"] == name


def test_create_new_bond_with_missing_name(client):
    name = str(uuid.uuid4())
    new_bond = dict(
        description=name,
        is_active=True,
        bond_expiration=dt.datetime(2021, 4, 5, 14, 34).isoformat(
            timespec="seconds"
        ),
        bond_value="12.123456",
    )
    resp = client.post("/asset/bond", json=new_bond)
    assert resp.status_code == 422


def test_create_new_bond_with_missing_description(client):
    name = str(uuid.uuid4())
    new_bond = dict(
        name=name,
        is_active=True,
        bond_expiration=dt.datetime(2021, 4, 5, 14, 34).isoformat(
            timespec="seconds"
        ),
        bond_value="12.123456",
    )
    resp = client.post("/asset/bond", json=new_bond)
    assert resp.status_code == 422


def test_create_new_bond_with_missing_is_active(client):
    name = str(uuid.uuid4())
    new_bond = dict(
        name=name,
        description=name,
        bond_expiration=dt.datetime(2021, 4, 5, 14, 34).isoformat(
            timespec="seconds"
        ),
        bond_value="12.123456",
    )
    resp = client.post("/asset/bond", json=new_bond)
    assert resp.status_code == 422


def test_create_new_bond_with_missing_expiration(client):
    name = str(uuid.uuid4())
    new_bond = dict(
        name=name,
        description=name,
        is_active=True,
        bond_value="12.123456",
    )
    resp = client.post("/asset/bond", json=new_bond)
    assert resp.status_code == 200


def test_create_new_bond_with_missing_value(client):
    name = str(uuid.uuid4())
    new_bond = dict(
        name=name,
        description=name,
        is_active=True,
        bond_expiration=dt.datetime(2021, 4, 5, 14, 34).isoformat(
            timespec="seconds"
        ),
    )
    resp = client.post("/asset/bond", json=new_bond)
    assert resp.status_code == 200


def test_create_new_bond_with_extra_data(client):
    name = str(uuid.uuid4())
    new_bond = dict(
        name=name,
        description=name,
        is_active=True,
        bond_expiration=dt.datetime(2021, 4, 5, 14, 34).isoformat(
            timespec="seconds"
        ),
        bond_value="12.123456",
        bogus_field="clakmcdsa",
    )
    resp = client.post("/asset/bond", json=new_bond)
    assert resp.status_code == 422


def test_edit_bonds(client):
    _, resp = create_new_bond(client)
    resp2 = client.get(f"/asset/{resp.json()['id']}")
    new_bond = resp2.json()

    edited_bond = copy.deepcopy(new_bond)
    edited_bond["description"] = "aaaaaaaaaaaaxxxxxxxxxxxx"
    del edited_bond["id"]
    del edited_bond["type"]
    resp2 = client.put(f"asset/bond/{new_bond['id']}", json=edited_bond)
    print(resp2.json())
    assert resp2.status_code == 200
    assert isinstance(resp2.json(), dict)
    for field in ["id", "name"]:
        assert resp2.json()[field] == new_bond[field]
    assert resp2.json()["description"] == "aaaaaaaaaaaaxxxxxxxxxxxx"


def test_bonds_accepts_str_with_10_decimals(client):
    name = str(uuid.uuid4())
    new_bond = dict(
        name=name,
        description=name,
        is_active=True,
        bond_value="12.0123456789",
    )
    resp = client.post("/asset/bond", json=new_bond)
    assert str(resp.json()["bond_value"]) == "12.0123456789"


def test_bonds_doesnt_accept_str_with_more_then_10_decimals(client):
    name = str(uuid.uuid4())
    new_bond = dict(
        name=name,
        description=name,
        is_active=True,
        bond_value="12.12345678901",
    )
    resp = client.post("/asset/bond", json=new_bond)
    assert resp.status_code == 422
