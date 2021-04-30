from datetime import datetime

from preacher.compilation.error import CompilationError
from preacher.compilation.util.type import ensure_str
from preacher.core.datetime import DatetimeWithFormat, system_timezone, parse_time, parse_timedelta
from preacher.core.value import Value
from preacher.core.value.impl.datetime import DatetimeValueWithFormat
from preacher.core.value.impl.datetime import OnlyTimeDatetime
from preacher.core.value.impl.datetime import RelativeDatetime
from preacher.core.value.impl.static import StaticValue


def compile_datetime_value_with_format(obj: object) -> Value[DatetimeWithFormat]:
    """
    Args:
        obj: The compiled value, which should be a datetime or a string.
    Raises:
        CompilationError: When compilation fails.
    """
    if isinstance(obj, datetime):
        if not obj.tzinfo:
            obj = obj.replace(tzinfo=system_timezone())
        return StaticValue(DatetimeWithFormat(obj))

    # Try to parse `obj` as a datetime-compatible string below.
    try:
        value = ensure_str(obj)
    except CompilationError as error:
        message = f'Must be a datetime-compatible value, but given {type(obj)}: {obj}'
        raise CompilationError(message, cause=error)

    try:
        tm = parse_time(value)
        return DatetimeValueWithFormat(OnlyTimeDatetime(tm))
    except ValueError:
        pass  # Try to compile value as another format.

    try:
        delta = parse_timedelta(value)
        return DatetimeValueWithFormat(RelativeDatetime(delta))
    except ValueError:
        pass  # Try to compile value as another format.

    raise CompilationError(f'Invalid format: {obj}')
