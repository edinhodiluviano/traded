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
