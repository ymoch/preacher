"""
Value interpretation.
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar('T')

_KEY_ARGUMENTS = "arguments"


class Value(ABC, Generic[T]):

    @abstractmethod
    def apply_context(self, **kwargs) -> T:
        raise NotImplementedError()


class StaticValue(Value[T]):

    def __init__(self, value: T):
        self._value = value

    def apply_context(self, **kwargs) -> T:
        return self._value


class ArgumentValue(Value[object]):

    def __init__(self, key: str):
        self._key = key

    def apply_context(self, **kwargs) -> object:
        return kwargs.get(_KEY_ARGUMENTS, {}).get(self._key)


def value_of(obj: T) -> Value[T]:
    return StaticValue(obj)
