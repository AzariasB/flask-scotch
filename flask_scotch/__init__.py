from typing import Optional

from flask import Flask

from .RemoteModel import RemoteModel
from .RemoteRelationship import RemoteRelationship
from .LocalRelationship import LocalRelationship
from .LocalModel import LocalModel

__version__ = "0.0.2"


class FlaskScotch:
    """
    Entrypoint of this library.

    The app instance is used to have access to the sqlAlchemy engine (if it exists), and to set
    the extension, so that it can be retrieved by the instances later on

    """

    def __init__(self, app: Optional[Flask] = None, api_url: Optional[str] = None, sql_engine=None):
        """


        :param app: The flask app instance, used to configure the extension and make it available
        :param api_url: The URL of the API to use when fetching the entities, if not given, the extension will use
        the value of the SCOTCH_API_URL config
        :param sql_engine: the SqlAlchemy engine to use to query the objects in the local database
        """
        self.app = app
        self.api_url = api_url
        self.sql_engine = sql_engine

        if app is not None:
            self.init_app(app)

        if self.api_url is not None:
            self.api_url = self.api_url.strip("/")

    def init_app(self, app: Flask):
        """
        Configures the missing pieces of the extension if needed base on the given app instance
        Tries to get the alchemy engine in the extensions dictionary.
        Also tries to configure the api url if it has not already been done

        :param app:
        :return:
        """
        self.app = app
        app.extensions["scotch"] = self

        if "sqlalchemy" in app.extensions:
            self.sql_engine = app.extensions["sqlalchemy"]

        if "SCOTCH_API_URL" in app.config:
            self.api_url = app.config.get("SCOTCH_API_URL")
