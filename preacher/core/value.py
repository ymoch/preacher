"""
Value interpretation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Generic, Optional, TypeVar

from preacher.core.datetime import DatetimeWithFormat, DatetimeFormat, ISO8601, now

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


class RelativeDatetime(Value[DatetimeWithFormat]):

    def __init__(
        self,
        delta: Optional[timedelta] = None,
        fmt: Optional[DatetimeFormat] = None,
    ):
        self._delta = delta or timedelta()
        self._fmt = fmt or ISO8601

    def resolve(
        self,
        context: Optional[ValueContext] = None,
    ) -> DatetimeWithFormat:
        if not context:
            context = ValueContext()

        origin = context.origin_datetime or now()
        return DatetimeWithFormat(origin + self._delta, self._fmt)
