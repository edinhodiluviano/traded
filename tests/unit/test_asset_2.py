def test_asset_get_all(client):
    resp = client.get("/asset")
    assert resp.status_code == 200
    assets = resp.json()
    assert isinstance(assets, list)


def test_asset_default_database(client):
    resp = client.get("/asset")
    assert len(resp.json()) > 0
