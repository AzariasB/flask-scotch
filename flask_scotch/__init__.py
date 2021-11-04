from typing import Optional

from flask import Flask

from .RemoteModel import RemoteModel

__version__ = "0.0.1"


class FlaskScotch:
    def __init__(self, app: Optional[Flask] = None, api_url: Optional[str] = None, sql_engine=None):
        self.app = app
        self.api_url = api_url
        self.sql_engine = sql_engine

        if app is not None:
            self.init_app(app)

        if self.api_url is not None:
            self.api_url = self.api_url.strip("/")

    def init_app(self, app: Flask):
        self.app = app
        app.extensions["scotch"] = self

        if "sqlalchemy" in app.extensions:
            self.sql_engine = app.extensions["sqlalchemy"]

        if "SCOTCH_API_URL" in app.config:
            self.api_url = app.config.get("SCOTCH_API_URL")
