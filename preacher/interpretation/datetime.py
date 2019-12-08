from datetime import datetime, timezone
from typing import Any, Optional

from preacher.core.datetime import now
from .timedelta import interpret_timedelta


def interpret_datetime(value: Optional[Any], **kwargs) -> datetime:
    if isinstance(value, datetime):
        if not value.tzinfo:
            return value.replace(tzinfo=timezone.utc)
        return value
    delta = interpret_timedelta(value)
    origin = kwargs.get('request_datetime') or now()
    return origin + delta
