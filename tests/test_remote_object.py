import pytest
import responses

from flask_scotch import RemoteModel

ITEMS = [
    {"id": 1, "name": "Car"},
    {"id": 2, "name": "Tire"},
    {"id": 3, "name": "Keyboard"},
    {"id": 4, "name": "Bottle"},
]


class Item(RemoteModel):
    __remote_directory__ = "items"

    id: int
    name: str


def test_init(app):
    with pytest.raises(AssertionError):
        get_api = Item.api
        assert get_api is not None


@responses.activate
def test_remote_object(app, scotch):
    responses.add(responses.GET, "http://localhost/items/", json=ITEMS)
    with app.test_request_context():
        res = Item.api.all()
        assert len(res) > 0
