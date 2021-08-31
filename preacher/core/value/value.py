from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar, Type

from preacher.core.context import Context

T = TypeVar("T")


class Value(ABC, Generic[T]):
    @property
    @abstractmethod
    def type(self) -> Type[T]:
        ...  # pragma: no cover

    @abstractmethod
    def resolve(self, context: Optional[Context] = None) -> T:
        ...  # pragma: no cover
