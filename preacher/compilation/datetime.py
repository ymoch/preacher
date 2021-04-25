"""Date and time compilation."""

import re
from datetime import time, timedelta

from preacher.core.datetime import DatetimeFormat, ISO8601, StrftimeFormat, system_timezone
from .error import CompilationError
from .util.type import ensure_str, ensure_optional_str

TIMEDELTA_PATTERN = re.compile(r'([+\-]?\d+)\s*(day|hour|minute|second)s?')


def compile_datetime_format(obj: object) -> DatetimeFormat:
    """
    Args:
        obj: The compiled value, which should be `None` or a string.
    Raises:
        CompilationError: When compilation fails.
    """
    format_string = ensure_optional_str(obj)
    if format_string is None or format_string.lower() == 'iso8601':
        return ISO8601
    return StrftimeFormat(format_string)


def compile_time(obj: object) -> time:
    """
    Args:
        obj: The compiled value, which should be a string.
    Raises:
        CompilationError: When compilation fails.
    """
    obj = ensure_str(obj)
    try:
        compiled = time.fromisoformat(obj)
    except ValueError:
        raise CompilationError(f'Invalid time format: {obj}')

    if not compiled.tzinfo:
        compiled = compiled.replace(tzinfo=system_timezone())
    return compiled


def compile_timedelta(obj: object) -> timedelta:
    """
    Args:
        obj: The compiled value, which should be a string.
    Raises:
        CompilationError: When compilation fails.
    """
    obj = ensure_str(obj)
    normalized = obj.strip().lower()
    if not normalized or normalized == 'now':
        return timedelta()

    match = TIMEDELTA_PATTERN.match(normalized)
    if not match:
        raise CompilationError(f'Invalid timedelta format: {obj}')
    offset = int(match.group(1))
    unit = match.group(2) + 's'
    return timedelta(**{unit: offset})
