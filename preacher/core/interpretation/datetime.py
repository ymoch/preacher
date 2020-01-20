"""
Datetime interpretation.
"""

from datetime import datetime, timezone

from preacher.core.datetime import now
from .timedelta import interpret_timedelta


def interpret_datetime(value: object, **kwargs) -> datetime:
    """
    Args:
        value (object): The interpreted value,
            which should be a datetime object or a string.
        **kwargs: options.
            - origin_datetime (datetime, optional):
              The origin of relative datetime.

    Raises:
        InterpretationError: When interpretation fails.
    """
    if isinstance(value, datetime):
        if not value.tzinfo:
            return value.replace(tzinfo=timezone.utc)
        return value

    delta = interpret_timedelta(value)
    origin = kwargs.get('origin_datetime') or now()
    return origin + delta
