from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar, Type, Union

from preacher.core.context import Context

T = TypeVar("T")


AnyContext = Context


class Value(ABC, Generic[T]):
    @property
    @abstractmethod
    def type(self) -> Type[T]:
        ...  # pragma: no cover

    @abstractmethod
    def resolve(self, context: Optional[Union[AnyContext]] = None) -> T:
        ...  # pragma: no cover
