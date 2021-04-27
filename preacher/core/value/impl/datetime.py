from datetime import time, datetime, timedelta
from typing import Optional, Type

from preacher.core.datetime import DatetimeWithFormat, DatetimeFormat, ISO8601, now
from preacher.core.value import Value, ValueContext


class OnlyTimeDatetime(Value[DatetimeWithFormat]):

    def __init__(self, tm: time, fmt: Optional[DatetimeFormat] = None):
        self._tm = tm
        self._fmt = fmt or ISO8601

    @property
    def type(self) -> Type[DatetimeWithFormat]:
        return DatetimeWithFormat

    def resolve(self, context: Optional[ValueContext] = None) -> DatetimeWithFormat:
        origin = _select_origin(context)
        return DatetimeWithFormat(datetime.combine(origin.date(), self._tm), self._fmt)


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

    def __init__(self, value: Value[datetime], fmt: Optional[DatetimeFormat] = None):
        self._value = value
        self._fmt = fmt or ISO8601

    @property
    def type(self) -> Type[DatetimeWithFormat]:
        return DatetimeWithFormat

    def resolve(self, context: Optional[ValueContext] = None) -> DatetimeWithFormat:
        resolved = self._value.resolve(context)
        return DatetimeWithFormat(resolved, self._fmt)


def _select_origin(context: Optional[ValueContext]) -> datetime:
    if not context:
        context = ValueContext()
    return context.origin_datetime or now()
