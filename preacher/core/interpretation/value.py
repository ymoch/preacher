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
    def resolve(self, **context) -> T:
        raise NotImplementedError()


class StaticValue(Value[T]):

    def __init__(self, value: T):
        self._value = value

    def resolve(self, **context) -> T:
        return self._value


class RelativeDatetimeValue(Value[datetime]):

    def __init__(self, delta: timedelta):
        self._delta = delta

    def resolve(self, **context) -> datetime:
        origin = context.get('origin_datetime') or now()
        return origin + self._delta
