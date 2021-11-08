import pytest
import responses
import json

from requests import PreparedRequest

from flask_scotch import RemoteModel

ITEMS = [
    {"id": 1, "name": "Car"},
    {"id": 2, "name": "Tire"},
    {"id": 3, "name": "Keyboard"},
    {"id": 4, "name": "Bottle"},
]


class Item(RemoteModel):
    __remote_directory__ = "items"

    name: str


def test_init(app):
    with pytest.raises(AssertionError):
        get_api = Item.api
        assert get_api is None


def _put_callback(request: PreparedRequest):
    if request.body is None:
        return 400, {}, json.dumps({"msg": "Failed"})

    decode = json.loads(request.body)

    found = next(iter(item for item in ITEMS if item["id"] == decode["id"]), None)
    if found:
        found.update(decode)
        return 200, {}, json.dumps({"msg": "Success"})

    return 400, {}, json.dumps({"msg": "Failed"})


def _post_callback(request: PreparedRequest):
    if request.body is None:
        return 400, {}, json.dumps({"msg": "Failed"})
    decode = json.loads(request.body)

    if "name" in decode:
        ITEMS.append(decode | {"id": len(ITEMS) + 1})
        return 200, {}, json.dumps({"msg": "Success"})

    return 400, {}, json.dumps({"msg": "Failed"})


@responses.activate
def test_remote_object_operations(app, scotch):
    responses.add(responses.GET, "http://localhost/items/", json=ITEMS)
    responses.add(responses.GET, "http://localhost/items/1", json=ITEMS[0])
    responses.add_callback(responses.PUT, "http://localhost/items/1", callback=_put_callback)
    responses.add_callback(responses.POST, "http://localhost/items/", callback=_post_callback)

    with app.test_request_context():
        res = Item.api.all()
        assert len(res) > 0
        assert all(isinstance(it, Item) for it in res)

        first: Item = Item.api.get(1)
        assert isinstance(first, Item)
        assert first.id == 1

        first.name = "Changed"
        first.update()
        assert ITEMS[0]["name"] == "Changed"

        nw = Item(name="Mouse")
        before = len(ITEMS)
        Item.api.create(nw)
        after = len(ITEMS)
        assert before + 1 == after
        assert ITEMS[-1]["name"] == "Mouse"
