from preacher.compilation.util import compile_optional_str
from preacher.core.datetime import DateTimeFormat, ISO8601, StrftimeFormat


def compile_datetime_format(obj: object) -> DateTimeFormat:
    """`obj` should be `None` or a string."""
    format_string = compile_optional_str(obj)
    if format_string is None or format_string.lower() == 'iso8601':
        return ISO8601
    return StrftimeFormat(format_string)
