from functools import lru_cache
from typing import Optional, Any


class ForeignModel:
    def __init__(self, remote_model: type[Any], key_attribute: Optional[str] = None):
        self.remote_model = remote_model
        self._key_attribute = key_attribute

    def __set_name__(self, owner, name):
        self._key_attribute = self._key_attribute or f"{name}_id"

    def retrieve_object(self, id_value: str):
        return self.remote_model.api.get(id_value)

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
            if isinstance(value, ForeignModel):
                self._setup_proxy(key, value)

    def _setup_proxy(self, key: str, value: ForeignModel):
        setattr(
            self.__class__,
            key,
            property(lru_cache(lambda this: value.retrieve_object(getattr(this, value.key_attribute())))),
        )
