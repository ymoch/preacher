from datetime import date

from preacher.core.datetime import DatetimeWithFormat


def to_serializable_value(value: object) -> object:
    if isinstance(value, DatetimeWithFormat):
        return value.formatted
    if isinstance(value, date):
        return value.isoformat()
    return value
