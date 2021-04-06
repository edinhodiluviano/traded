def test_should_always_pass():
    pass


def test_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), dict)
