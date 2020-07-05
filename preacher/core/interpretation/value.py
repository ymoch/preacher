"""
Value interpretation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Generic, Optional, TypeVar

from preacher.core.datetime import (
    DateTimeWithFormat,
    DateTimeFormat,
    ISO8601,
    now,
)

T = TypeVar('T')


@dataclass(frozen=True)
class ValueContext:
    origin_datetime: Optional[datetime] = None


class Value(ABC, Generic[T]):

    @abstractmethod
    def resolve(self, context: Optional[ValueContext] = None) -> T:
        raise NotImplementedError()


class StaticValue(Value[T]):

    def __init__(self, value: T):
        self._value = value

    def resolve(self, context: Optional[ValueContext] = None) -> T:
        return self._value


class RelativeDatetimeValue(Value[DateTimeWithFormat]):

    def __init__(self, delta: timedelta, fmt: Optional[DateTimeFormat] = None):
        self._delta = delta
        self._fmt = fmt or ISO8601

    def resolve(
        self,
        context: Optional[ValueContext] = None,
    ) -> DateTimeWithFormat:
        if not context:
            context = ValueContext()

        origin = context.origin_datetime or now()
        return DateTimeWithFormat(origin + self._delta, self._fmt)
