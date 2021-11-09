from flask_scotch import ForeignModel, RemoteModel, PartialModel
import sqlalchemy as sa
import json
import responses


@responses.activate
def test_remote_object_operations(app, scotch, db):
    class Car(RemoteModel):
        __remote_directory__ = "cars"

        name: str

    class Tire(PartialModel, db.Model):
        __tablename__ = "tire"

        id = sa.Column(sa.Integer, primary_key=True)
        car_id = sa.Column(sa.Integer)

        car = ForeignModel(Car)

    CARS: list[Car] = []

    responses.add_callback(responses.GET, "http://localhost/cars/", callback=lambda r: (200, {}, json.dumps(CARS)))
    responses.add_callback(responses.GET, "http://localhost/cars/1", callback=lambda r: (200, {}, CARS[0].json()))

    with app.test_request_context():
        db.create_all()
        CARS.append(Car(id=1, name="My car"))

        tire = Tire(car_id=1)
        db.session.add(tire)
        db.session.commit()

        assert tire.car is not None

        assert tire.car == CARS[0]

        second_tire = Tire(car_id=1)
        assert second_tire.car == CARS[0]
