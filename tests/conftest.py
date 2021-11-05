import flask
import pytest

from flask_sqlalchemy import SQLAlchemy
from flask_scotch import FlaskScotch


@pytest.fixture
def app(request):
    app = flask.Flask(request.module.__name__)
    app.testing = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    return app


@pytest.fixture
def db(app):
    return SQLAlchemy(app)


@pytest.fixture
def scotch(app, db):
    return FlaskScotch(app, "http://localhost", db)
