from functools import lru_cache
from typing import Any, Union, Optional

from flask_scotch.utils import local_model_from_name


class LocalRelationship:
    """
    Ease access to local objets, when using a remoteModel that has some objects that are in the local database

    When the remote object has only one local object :
        - query is select * from local_model where <remote_object_field_id> = remote_object.id limit 1

    When the remote object has several local objets, same query, without limit
    When the remote object is only linked to one

    Trois cas à gérer:
     - 1 to 1 : un objet remote est associé à un seul objet en BDD
     - 1:M : un objet remote est associé à M objets en BDD
     - M:1 : un objet en BDD est associé à M objets remote

    """

    def __init__(self, local_model: Union[str, type[Any]], database_field_name: Optional[str] = None, use_list=True):
        self.local_model = local_model
        self.database_field_name = database_field_name
        self.use_list = use_list

    def __set_name__(self, owner, name):
        if self.database_field_name is None:
            self.database_field_name = f"{owner.__name__}_id"

    @lru_cache
    def _local_class(self):
        return local_model_from_name(self.local_model)

    def get_query(self, remote_instance: Any):
        def _callback():
            if self.database_field_name is None:
                raise ValueError("Database field name not set.")

            # Fetch the object
            query_args = {self.database_field_name: remote_instance.id}
            query = self._local_class().query.filter_by(**query_args)
            return query.all() if self.use_list else query.first()

        return _callback
