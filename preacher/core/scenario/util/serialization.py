from datetime import date

from preacher.core.datetime import DateTime


def to_serializable_value(value: object) -> object:
    if isinstance(value, DateTime):
        return value.formatted
    if isinstance(value, date):
        return value.isoformat()
    return value
