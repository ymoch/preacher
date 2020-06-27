from abc import ABC, abstractmethod
from typing import Any


class RequestBody(ABC):

    @property
    @abstractmethod
    def content_type(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def resolve(self, **kwargs) -> Any:
        raise NotImplementedError()
