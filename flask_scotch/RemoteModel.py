from typing import Optional, Any
from flask import current_app
from urllib import parse
from os import path
import requests

from pydantic import BaseModel, Extra, PrivateAttr
from functools import lru_cache


class ApiAccessor:
    def __init__(self, model: type["RemoteModel"]):
        if not current_app or not current_app.extensions["scotch"]:
            raise AssertionError("Scotch extension not registered")
        self.model = model
        self.api_url = parse.urlparse(current_app.extensions["scotch"].api_url)

    def _build_url(self, subdirectory: str = "", parameters: Optional[dict[Any, Any]] = None):
        url_path = path.join(self.api_url.path, self.model.__remote_directory__, subdirectory)
        if parameters is not None:
            query = parse.urlencode(parameters)
        else:
            query = ""

        constructed_url = parse.ParseResult(
            scheme=self.api_url.scheme,
            netloc=self.api_url.netloc,
            path=url_path,
            query=query,
            params="",
            fragment="",
        )
        return constructed_url.geturl()

    def _request(self, verb: str, subdirectory="", url_params: Optional[dict[Any, Any]] = None, **kwargs):
        url = self._build_url(subdirectory, url_params)
        if verb == "get":
            response = requests.get(url, **kwargs)
            return response.json()
        if verb == "post":
            response = requests.post(url, **kwargs)
            return response.json()
        if verb == "put":
            response = requests.put(url, **kwargs)
            return response.json()
        if verb == "delete":
            response = requests.delete(url, **kwargs)
            return response.json()
        raise TypeError(f"Unknown verb {verb}")

    def all(self, **kwargs):
        entities = self._request("get", **kwargs)
        return list(self.model.parse_obj(item) for item in entities)

    def get(self, model_id: int):
        entity = self._request("get", str(model_id))
        return self.model.parse_obj(entity)

    def update(self, entity: "RemoteModel"):
        return self._request("put", str(entity.id), data=entity.json())

    def delete(self, model_id: int):
        return self._request("delete", str(model_id))

    def create(self, entity: "RemoteModel"):
        res = self._request("post", data=entity.json())
        if res.get("msg", None) == "Success":
            return entity
        raise ValueError("Failed to create entity")


class RemoteModel(BaseModel):
    """
    Class used to describe a model that can be accessed via the remote API.

    It uses pydantic to tranform the json response into a python class instance.
    To declare the fields available in the json, only the type definition of these
    fields is needed.
    Example:

    class Computer(RemoteModel):
        model: str
        cpu: str
        year: int


    RemoteModel automatically adds an "id" attribute as a sort of primary key used to retrieve
    the object in the remote API as well as (if needed) in the local databse)

    """

    class Config:
        arbitrary_types_allowed = True
        extra = Extra.allow

    __remote_directory__: str
    api: ApiAccessor
    _proxies = PrivateAttr()

    id: Optional[int]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        assert (
            hasattr(self, "__remote_directory__") and self.__remote_directory__ is not None
        ), "A remote model must have a directory path set"
        self._proxies = dict()
        self.instantiate_local_models()

    def instantiate_local_models(self):
        from flask_scotch import LocalRelationship

        attributes = [key for key in dir(self) if not key.startswith("__")]
        for key in attributes:
            value = getattr(self, key)
            if isinstance(value, LocalRelationship):
                self._setup_proxy(key, value)

    def _setup_proxy(self, key, model):
        delattr(self, key)
        self._proxies[key] = model.get_query(self)

    def __getattr__(self, item):
        if item in self._proxies:
            instance = self._proxies[item]()
            setattr(self, item, instance)
            return instance

        return super().__getattr__(item)

    @classmethod  # type: ignore
    @property
    @lru_cache
    def api(cls) -> ApiAccessor:
        """
        Access to the object used to query the remote API,
        the ApiAccessor can be used to fetch, update, create and delete data in the remote API

        :return: ApiAccessor
        """
        accessor = ApiAccessor(cls)
        return accessor

    def update(self):
        """
        Creates and sends an HTTP request to update the data to the remote API

        :return:
        """
        return self.api.update(self)

    def delete(self):
        """
        Create and sends an HTTP request to delete the model from the remote API

        :return:
        """
        return self.api.delete(self.id)
