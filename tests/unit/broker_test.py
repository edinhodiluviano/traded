import uuid


def test_should_always_pass():
    pass


def _check_valid_broker(broker):
    assert isinstance(broker, dict)
    for field, type_ in dict(id=int, name=str).items():
        assert field in broker
        assert isinstance(broker[field], type_)


def test_create_broker(client):
    name = str(uuid.uuid4())
    broker_create = dict(name=name)
    resp = client.post("/broker", json=broker_create)
    print(resp.json())
    assert resp.status_code == 200
    broker = resp.json()
    _check_valid_broker(broker)
    return broker


def test_get_broker(client):
    resp = client.get("/broker")
    assert resp.status_code == 200
    brokers = resp.json()
    assert isinstance(brokers, list)
    len_before = len(brokers)

    test_create_broker(client)

    resp = client.get("/broker")
    brokers = resp.json()
    len_after = len(brokers)
    for broker in brokers:
        _check_valid_broker(broker)

    assert len_before + 1 == len_after


def test_get_by_id(client):
    broker = test_create_broker(client)
    resp = client.get(f"/broker/{broker['id']}")
    assert resp.status_code == 200
    broker_got = resp.json()
    _check_valid_broker(broker_got)
    assert broker_got == broker


def test_update_broker(client):
    broker = test_create_broker(client)
    name = str(uuid.uuid4())
    new_broker = {"name": name}
    resp = client.put(f"/broker/{broker['id']}", json=new_broker)
    print(resp.json())
    assert resp.status_code == 200
    new_broker_got = resp.json()
    _check_valid_broker(new_broker_got)
    assert new_broker_got["name"] == name
    assert new_broker_got["name"] != broker["name"]
