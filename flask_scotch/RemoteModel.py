from typing import Optional, Any
from flask import current_app
from urllib import parse
from os import path
import requests

from pydantic import BaseModel
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
    __remote_directory__: str
    api: ApiAccessor

    id: Optional[int]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        assert (
            hasattr(self, "__remote_directory__") and self.__remote_directory__ is not None
        ), "A remote model must have a directory path set"

    @classmethod  # type: ignore
    @property
    @lru_cache
    def api(cls) -> ApiAccessor:
        accessor = ApiAccessor(cls)
        return accessor

    def update(self):
        return self.api.update(self)

    def delete(self):
        return self.api.delete(self.id)
