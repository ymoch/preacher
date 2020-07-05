"""
Value interpretation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Generic, Optional, TypeVar

from preacher.core.datetime import DateTimeWithFormat, now

T = TypeVar('T')

_KEY_ARGUMENTS = "arguments"


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

    def __init__(self, delta: timedelta):
        self._delta = delta

    def resolve(
        self,
        context: Optional[ValueContext] = None,
    ) -> DateTimeWithFormat:
        if not context:
            context = ValueContext()

        origin = context.origin_datetime or now()
        return DateTimeWithFormat(origin + self._delta)
