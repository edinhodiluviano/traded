def test_asset_get_all(client):
    resp = client.get("/asset")
    assert resp.status_code == 200
    assets = resp.json()
    assert isinstance(assets, list)