from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Generic, Optional, TypeVar, Type, Union

from preacher.core.context import Context

T = TypeVar("T")


@dataclass(frozen=True)
class ValueContext:
    origin_datetime: Optional[datetime] = None


AnyContext = Union[ValueContext, Context]


class Value(ABC, Generic[T]):
    @property
    @abstractmethod
    def type(self) -> Type[T]:
        ...  # pragma: no cover

    @abstractmethod
    def resolve(self, context: Optional[Union[AnyContext]] = None) -> T:
        ...  # pragma: no cover
