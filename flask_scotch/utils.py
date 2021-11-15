import inspect
from typing import Any, Union, cast


def all_subclasses(cls: type[Any]):
    return set(cls.__subclasses__()).union([s for c in cls.__subclasses__() for s in all_subclasses(c)])


def class_from_name(name: Union[str, type[Any]], parent_class: type[Any]) -> type[Any]:
    """
    Retrieves a class from the name.
    Used by LocalRelationShip and RemoteRelationship when the name of the model passed
    is a string

    When the model passed in parameter is a class, it is returned without any further validation

    If no class with the given name is found, raises a ValueError

    :param name: the class or the name of the class
    :param parent_class: the root class from where to search for the class with the given name
    :return: the class that inherits the parent_class
    """
    if inspect.isclass(name):
        return cast(type[Any], name)
    all_known_classes = all_subclasses(parent_class)

    found = next(iter(cls for cls in all_known_classes if cls.__name__ == name), None)
    if found is None:
        raise ValueError(f"Failed to find class with name {name}, is it a subclass of {parent_class.__name__} ?")

    return found


def remote_model_from_name(name: Union[str, type[Any]]) -> type[Any]:
    """
    Used by LocalRelationship to retrieve a remotemodel from the name or the class
    :param name:
    :return:
    """
    from .RemoteModel import RemoteModel

    return class_from_name(name, RemoteModel)


def local_model_from_name(name: Union[str, type[Any]]) -> type[Any]:
    """
    Used by RemoteRelationship to retrieve a LocalModel from the name or the class

    :param name:
    :return:
    """
    from .LocalModel import LocalModel

    return class_from_name(name, LocalModel)
