from functools import lru_cache

from .RemoteRelationship import RemoteRelationship


class LocalModel:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._configure_foreign_models()

    def _configure_foreign_models(self):
        attributes = [key for key in dir(self) if not key.startswith("__")]
        for key in attributes:
            value = getattr(self, key)
            if isinstance(value, RemoteRelationship):
                self._setup_proxy(key, value)

    def _setup_proxy(self, key: str, value: RemoteRelationship):
        setattr(
            self.__class__,
            key,
            property(lru_cache(lambda this: value.retrieve_object(getattr(this, value.key_attribute())))),
        )
