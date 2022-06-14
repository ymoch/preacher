"""Date and time compilation."""

from datetime import timedelta

from preacher.core.datetime import DatetimeFormat, parse_timedelta
from preacher.core.datetime import ISO8601
from preacher.core.datetime import StrftimeFormat
from .error import CompilationError
from .util.type import ensure_optional_str, ensure_str


def compile_datetime_format(obj: object) -> DatetimeFormat:
    """
    Args:
        obj: The compiled value, which should be `None` or a string.
    Raises:
        CompilationError: When compilation fails.
    """
    format_string = ensure_optional_str(obj)
    if format_string is None or format_string.lower() == "iso8601":
        return ISO8601
    return StrftimeFormat(format_string)


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
        raise CompilationError(str(error), cause=error)
