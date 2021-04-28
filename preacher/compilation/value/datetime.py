from datetime import datetime

from preacher.compilation.datetime import compile_time, compile_timedelta
from preacher.compilation.error import CompilationError
from preacher.core.datetime import DatetimeWithFormat, system_timezone
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

    try:
        tm = compile_time(obj)
        return DatetimeValueWithFormat(OnlyTimeDatetime(tm))
    except CompilationError:
        pass  # Try to compile value as another format.

    try:
        delta = compile_timedelta(obj)
        return DatetimeValueWithFormat(RelativeDatetime(delta))
    except CompilationError:
        pass  # Try to compile value as another format.

    raise CompilationError(f'Invalid format: {obj}')
