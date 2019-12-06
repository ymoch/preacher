from abc import ABC, abstractmethod
from typing import TypeVar, Generic


T = TypeVar('T')


class Value(ABC, Generic[T]):

    @abstractmethod
    def apply_context(self, **kwargs) -> T:
        raise NotImplementedError()


class StaticValue(Value[T]):

    def __init__(self, value: T):
        self._value = value

    def apply_context(self, **kwargs) -> T:
        return self._value
