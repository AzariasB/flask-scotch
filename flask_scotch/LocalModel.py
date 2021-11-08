from typing import Any

_empty_instance = object()


class LocalModel:
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

    def __init__(self, local_model: type[Any], database_field_name: str, use_list=True):
        self.local_model = local_model
        self.database_field_name = database_field_name
        self.use_list = use_list

    def get_query(self, remote_instance: Any):
        def _callback():
            # Fetch the object
            query_args = {self.database_field_name: remote_instance.id}
            query = self.local_model.query.filter_by(**query_args)
            return query.all() if self.use_list else query.first()

        return _callback