"""Date and time compilation."""

import re

from preacher.core.datetime import DatetimeFormat
from preacher.core.datetime import ISO8601
from preacher.core.datetime import StrftimeFormat
from .util.type import ensure_optional_str

TIMEDELTA_PATTERN = re.compile(r"([+\-]?\d+)\s*(day|hour|minute|second)s?")


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
