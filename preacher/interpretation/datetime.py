from datetime import datetime
from typing import Any, Optional

from preacher.core.datetime import now
from .timedelta import interpret_timedelta


def interpret_datetime(value: Optional[Any], **kwargs) -> datetime:
    delta = interpret_timedelta(value)
    origin = kwargs.get('request_datetime') or now()
    return origin + delta
