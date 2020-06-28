from datetime import datetime


def to_serializable_value(value: object) -> object:
    if isinstance(value, datetime):
        return value.isoformat()
    return value
