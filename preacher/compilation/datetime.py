"""Date and time compilation."""

import re
from datetime import time, timedelta

from preacher.core.datetime import DatetimeFormat
from preacher.core.datetime import StrftimeFormat
from preacher.core.datetime import ISO8601
from preacher.core.datetime import parse_time
from preacher.core.datetime import parse_timedelta
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
    value = ensure_str(obj)
    try:
        return parse_time(value)
    except ValueError as error:
        raise CompilationError(f'Invalid time format: {obj}', cause=error)


def compile_timedelta(obj: object) -> timedelta:
    """
    Args:
        obj: The compiled value, which should be a string.
    Raises:
        CompilationError: When compilation fails.
    """
    value = ensure_str(obj)
    try:
        return parse_timedelta(value)
    except ValueError as error:
        raise CompilationError(f'Invalid timedelta format: {obj}', cause=error)
