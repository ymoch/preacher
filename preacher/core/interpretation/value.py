"""
Value interpretation.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import TypeVar, Generic

from preacher.core.datetime import now

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


class RelativeDatetimeValue(Value[datetime]):

    def __init__(self, delta: timedelta):
        self._delta = delta

    def apply_context(self, **kwargs) -> datetime:
        origin = kwargs.get('origin_datetime') or now()
        return origin + self._delta
