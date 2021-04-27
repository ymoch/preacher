from datetime import time, datetime, timedelta
from typing import Optional, Type

from preacher.core.datetime import DatetimeWithFormat, DatetimeFormat, ISO8601, now
from preacher.core.value import Value, ValueContext


class OnlyTimeDatetime(Value[datetime]):

    def __init__(self, tm: time):
        self._tm = tm

    @property
    def type(self) -> Type[datetime]:
        return datetime

    def resolve(self, context: Optional[ValueContext] = None) -> datetime:
        origin = _select_origin(context)
        return datetime.combine(origin.date(), self._tm)


class RelativeDatetime(Value[datetime]):

    def __init__(self, delta: Optional[timedelta] = None):
        self._delta = delta or timedelta()

    @property
    def type(self) -> Type[datetime]:
        return datetime

    def resolve(self, context: Optional[ValueContext] = None) -> datetime:
        origin = _select_origin(context)
        return origin + self._delta


class DatetimeValueWithFormat(Value[DatetimeWithFormat]):

    def __init__(self, original: Value[datetime], fmt: Optional[DatetimeFormat] = None):
        self._original = original
        self._fmt = fmt or ISO8601

    @property
    def type(self) -> Type[DatetimeWithFormat]:
        return DatetimeWithFormat

    def resolve(self, context: Optional[ValueContext] = None) -> DatetimeWithFormat:
        resolved = self._original.resolve(context)
        return DatetimeWithFormat(resolved, self._fmt)


def _select_origin(context: Optional[ValueContext]) -> datetime:
    if not context:
        context = ValueContext()
    return context.origin_datetime or now()
