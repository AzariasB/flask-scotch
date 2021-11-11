from flask_scotch import RemoteRelationship, RemoteModel, LocalModel, LocalRelationship
import sqlalchemy as sa
import json
import re
import responses


@responses.activate
def test_remote_object_operations(app, scotch, db):
    class Car(RemoteModel):
        __remote_directory__ = "cars"

        name: str

    class Tire(LocalModel, db.Model):
        __tablename__ = "tire"

        id = sa.Column(sa.Integer, primary_key=True)
        car_id = sa.Column(sa.Integer)

        car = RemoteRelationship(Car)

    CARS: list[Car] = []

    def _get_car(req):
        car_id = int(req.path_url[6:])
        return 200, {}, CARS[car_id - 1].json()

    responses.add_callback(responses.GET, "http://localhost/cars/", callback=lambda r: (200, {}, json.dumps(CARS)))
    responses.add_callback(responses.GET, re.compile(r"http://localhost/cars/(\d*)"), callback=_get_car)

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

        assert tire.car == CARS[0]

        CARS.append(Car(id=2, name="Second car"))

        s_tire = Tire(car_id=2)
        assert s_tire.car == CARS[-1]

        empty_tire = Tire()
        assert empty_tire.car is None


@responses.activate
def test_string_referencing(app, scotch, db):
    class Author(RemoteModel):
        __remote_directory__ = "authors"

        name: str
        books = LocalRelationship("Book", "author_id")

    class Book(LocalModel, db.Model):
        __tablename__ = "book"

        id = sa.Column(sa.Integer, primary_key=True)
        author_id = sa.Column(sa.Integer)

        author = RemoteRelationship("Author")

    AUTHORS: list[Author] = []

    def _get_author(req):
        start_ = len("authors") + 2
        car_id = int(req.path_url[start_:])
        return 200, {}, AUTHORS[car_id - 1].json()

    responses.add_callback(
        responses.GET, "http://localhost/authors/", callback=lambda r: (200, {}, json.dumps(AUTHORS))
    )
    responses.add_callback(responses.GET, re.compile(r"http://localhost/authors/(\d*)"), callback=_get_author)

    with app.test_request_context():
        db.create_all()
        AUTHORS.append(Author(id=1, name="Someone"))

        book = Book(id=1, author_id=1)
        assert book.author == AUTHORS[0]

        db.session.add(book)
        db.session.commit()

        assert AUTHORS[0].books == [book]

        db.session.delete(book)
        db.session.commit()

        # Assert we're not querying the database again
        assert AUTHORS[0].books == [book]

        # Back to querying
        assert Author(id=1, name="Someone").books == []
