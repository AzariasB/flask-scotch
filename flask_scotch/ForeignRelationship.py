from functools import lru_cache
from typing import Optional, Any, Union

from flask_scotch.utils import remote_model_from_name


class ForeignRelationship:
    def __init__(self, remote_model: Union[type[Any], str], key_attribute: Optional[str] = None):
        self.remote_model = remote_model
        self._key_attribute = key_attribute

    def __set_name__(self, owner, name):
        self._key_attribute = self._key_attribute or f"{name}_id"

    @lru_cache
    def _remote_class(self):
        return remote_model_from_name(self.remote_model)

    def retrieve_object(self, id_value: str):
        return self._remote_class().api.get(id_value)

    def key_attribute(self):
        if self._key_attribute is None:
            raise ValueError("Attribute used to retrieve the foreign model was not set on the Foreign Model")
        return self._key_attribute


class PartialModel:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._configure_foreign_models()

    def _configure_foreign_models(self):
        attributes = [key for key in dir(self) if not key.startswith("__")]
        for key in attributes:
            value = getattr(self, key)
            if isinstance(value, ForeignRelationship):
                self._setup_proxy(key, value)

    def _setup_proxy(self, key: str, value: ForeignRelationship):
        setattr(
            self.__class__,
            key,
            property(lru_cache(lambda this: value.retrieve_object(getattr(this, value.key_attribute())))),
        )
