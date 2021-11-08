from typing import Any


class ForeignModel:
    def __init__(self, remote_model: type[Any]):
        self.remote_model = remote_model
