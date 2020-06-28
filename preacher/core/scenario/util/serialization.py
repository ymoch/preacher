from datetime import date


def to_serializable_value(value: object) -> object:
    if isinstance(value, date):
        return value.isoformat()
    return value
