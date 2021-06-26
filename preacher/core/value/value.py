from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Generic, Optional, TypeVar, Type

T = TypeVar("T")


@dataclass(frozen=True)
class ValueContext:
    origin_datetime: Optional[datetime] = None


class Value(ABC, Generic[T]):
    @property
    @abstractmethod
    def type(self) -> Type[T]:
        ...  # pragma: no cover

    @abstractmethod
    def resolve(self, context: Optional[ValueContext] = None) -> T:
        ...  # pragma: no cover
