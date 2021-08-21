from datetime import time, datetime, timedelta
from typing import Optional, Type

from preacher.core.datetime import DatetimeWithFormat
from preacher.core.datetime import DatetimeFormat
from preacher.core.datetime import ISO8601
from preacher.core.datetime import now
from preacher.core.datetime import parse_time
from preacher.core.datetime import parse_timedelta
from preacher.core.datetime import system_timezone
from preacher.core.value import Value, ValueContext
from .static import StaticValue


class RelativeDatetime(Value[datetime]):
    def __init__(self, delta: Optional[timedelta] = None, tm: Optional[time] = None):
        self._delta = delta or timedelta()
        self._tm = tm

    @property
    def type(self) -> Type[datetime]:
        return datetime

    def resolve(self, context: Optional[ValueContext] = None) -> datetime:
        origin = _select_origin(context)
        resolved = origin + self._delta
        if self._tm:
            resolved = datetime.combine(resolved.date(), self._tm)
        return resolved


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


def parse_datetime_value_with_format(
    value: object,
    fmt: Optional[DatetimeFormat] = None,
) -> Value[DatetimeWithFormat]:
    """
    Args:
        value: The compiled value, which should be a datetime or a string.
        fmt: The datetime format.
    Raises:
        ValueError: When parsing fails.
    """
    if isinstance(value, datetime):
        if not value.tzinfo:
            value = value.replace(tzinfo=system_timezone())
        return StaticValue(DatetimeWithFormat(value, fmt))

    # Try to parse `obj` as a datetime-compatible string below.
    if not isinstance(value, str):
        raise ValueError(f"Must be a datetime-compatible value, but given {type(value)}: {value}")

    try:
        tm = parse_time(value)
        return DatetimeValueWithFormat(RelativeDatetime(tm=tm), fmt)
    except ValueError:
        pass  # Try to compile value as another format.

    try:
        delta = parse_timedelta(value)
        return DatetimeValueWithFormat(RelativeDatetime(delta), fmt)
    except ValueError:
        raise ValueError(f"Invalid format: {value}")


def _select_origin(context: Optional[ValueContext]) -> datetime:
    if not context:
        context = ValueContext()
    return context.origin_datetime or now()
