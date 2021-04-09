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
