from functools import lru_cache
from typing import Optional, Any, Union

from flask_scotch.utils import remote_model_from_name


class RemoteRelationship:
    """
    Class used to represent a model that is accessible via the API.

    When accessed for the first time, it will send a request to get the data from the API.
    Once the model has been fetched, it can be updated locally before creating a new request to update it

    """

    def __init__(self, remote_model: Union[type[Any], str], key_attribute: Optional[str] = None):
        """
        Examples of usage:

        class Tire(LocalModel, db.Model):
            car_id = Column(db.Int)

            car = RemoteRelationship("Car")

        tire = Tire.get(1)

        tire.car

        :param remote_model: a string or directly the class to use as a remote api accessor
        to fetch the entities when needed
        :param key_attribute: the name of the local attribute to use when fetching the remote model.
        By default is equal to the
        name of the attribute + "_id"
        """

        self.remote_model = remote_model
        self._key_attribute = key_attribute

    def __set_name__(self, owner, name):
        self._key_attribute = self._key_attribute or f"{name}_id"

    @lru_cache
    def _remote_class(self):
        return remote_model_from_name(self.remote_model)

    def retrieve_object(self, id_value: Optional[str]):
        return None if id_value is None else self._remote_class().api.get(id_value)

    def key_attribute(self):
        if self._key_attribute is None:
            raise ValueError("Attribute used to retrieve the foreign model was not set on the Foreign Model")
        return self._key_attribute
