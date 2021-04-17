def test_get(client):
    resp = client.get("/account/?name=Cash")
    assert resp.status_code == 200
    account = resp.json()
    assert isinstance(account, dict)
    assert account["name"] == "Cash"
    assert isinstance(account["id"], int)


def test_get_with_invalid_account(client):
    resp = client.get("/account/?name=xxxxx")
    assert resp.status_code == 404


def test_get_without_name(client):
    resp = client.get("/account")
    assert resp.status_code == 422


def test_root_id_is_1(client):
    resp = client.get("/account/?name=root")
    assert resp.status_code == 200
    assert resp.json()["id"] == 1
