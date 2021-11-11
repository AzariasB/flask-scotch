import inspect
from typing import Any, Union


def all_subclasses(cls):
    return set(cls.__subclasses__()).union([s for c in cls.__subclasses__() for s in all_subclasses(c)])


def class_from_name(name: Union[str, type[Any]], parent_class):
    if inspect.isclass(name):
        return name
    all_known_classes = all_subclasses(parent_class)

    found = next(iter(cls for cls in all_known_classes if cls.__name__ == name), None)
    if found is None:
        raise ValueError(f"Failed to find class with name {name}, is it a subclass of {parent_class.__name__} ?")

    return found


def remote_model_from_name(name: Union[str, type[Any]]):
    from .RemoteModel import RemoteModel

    return class_from_name(name, RemoteModel)


def local_model_from_name(name: Union[str, type[Any]]):
    from .LocalModel import LocalModel

    return class_from_name(name, LocalModel)
