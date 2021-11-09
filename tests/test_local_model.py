from typing import Any

import responses
import json

from requests import PreparedRequest
import sqlalchemy as sa

from flask_scotch import RemoteModel, LocalRelationship

CARS: list[Any] = []


def _put_callback(request: PreparedRequest):
    if request.body is None:
        return 400, {}, json.dumps({"msg": "Failed"})

    decode = json.loads(request.body)

    found = next(iter(item for item in CARS if item["id"] == decode["id"]), None)
    if found:
        found.update(decode)
        return 200, {}, json.dumps({"msg": "Success"})

    return 400, {}, json.dumps({"msg": "Failed"})


def _post_callback(request: PreparedRequest):
    if request.body is None:
        return 400, {}, json.dumps({"msg": "Failed"})
    decode = json.loads(request.body)

    if "name" in decode:
        CARS.append(decode | {"id": len(CARS) + 1})
        return 200, {}, json.dumps({"msg": "Success"})

    return 400, {}, json.dumps({"msg": "Failed"})


@responses.activate
def test_attached(app, db, scotch):
    responses.add_callback(responses.GET, "http://localhost/cars/", callback=lambda r: (200, {}, json.dumps(CARS)))
    responses.add_callback(responses.GET, "http://localhost/cars/1", callback=lambda r: (200, {}, json.dumps(CARS[0])))
    responses.add_callback(responses.PUT, "http://localhost/cars/1", callback=_put_callback)
    responses.add_callback(responses.POST, "http://localhost/cars/", callback=_post_callback)

    class Tire(db.Model):
        __tablename__ = "tire"

        id = sa.Column(sa.Integer, primary_key=True)
        car_id = sa.Column(sa.Integer)

    class Car(RemoteModel):
        __remote_directory__ = "cars"

        name: str
        tires = LocalRelationship(Tire, "car_id")

    with app.test_request_context():
        db.create_all()

        nw_car = Car(name="voila")
        Car.api.create(nw_car)

        tires = nw_car.tires
        assert tires is not None
        assert len(tires) == 0

        one_tire = Tire()
        db.session.add(one_tire)
        db.session.commit()

        created_car = Car.api.all().pop(0)
        assert created_car is not None

        one_tire.car_id = created_car.id
        for _ in range(3):
            tire = Tire(car_id=created_car.id)
            db.session.add(tire)

        db.session.commit()

        car_tires = created_car.tires
        assert len(car_tires) == 4
