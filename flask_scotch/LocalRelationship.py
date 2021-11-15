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

    Exemple of use case

    class Car(RemoteModel):
        tires = LocalRelationship(Tire)

    my_car = Car.api.get(1)

    my_car_tires = my_car.tires

    Trois cas à gérer:
     - 1 to 1 : un objet remote est associé à un seul objet en BDD
     - 1:M : un objet remote est associé à M objets en BDD
     - M:1 : un objet en BDD est associé à M objets remote

    """

    def __init__(self, local_model: Union[str, type[Any]], database_field_name: Optional[str] = None, use_list=True):
        """
        Exemples :

        class Book(RemoteModel):
            author_id

            # Fetches the author in the database from the table associated to the Author model, where the author_id is
            # the same as  the book's
            author = LocalRelationship("Author", use_list=False)

        class A(RemoteModel):
            id: int

            # Fetches all the "B" instances where the field "custom_id" equals the id of A
            b = LocalRelationship("B", "custom_id")

        :param local_model: The Model to use to fetch the data from the database, can be directly the class,
        or the name of the class as a string
        :param database_field_name: The name of the field in the database to use to retrieve the the instance(s)
         of the object
        :param use_list: when fetching the entity from the database, to indicate wether a single instance is expected,
        or if a list of instances is expected
        """
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
