from datetime import date

from preacher.core.datetime import DateTimeWithFormat


def to_serializable_value(value: object) -> object:
    if isinstance(value, DateTimeWithFormat):
        return value.formatted
    if isinstance(value, date):
        return value.isoformat()
    return value
