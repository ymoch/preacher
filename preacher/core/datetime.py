"""
Datetime utilities for Preacher core.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import time

import aniso8601

_FORMAT_ISO8601 = 'iso8601'


class DateTime:

    def __init__(self, value: datetime, format: str = _FORMAT_ISO8601):
        self._value = value
        self._format = format

    @property
    def value(self) -> datetime:
        return self._value

    @property
    def formatted(self) -> str:
        if self._format == _FORMAT_ISO8601:
            return self._value.isoformat()
        return self._value.strftime(self._format)

    @staticmethod
    def now(format: str = _FORMAT_ISO8601) -> DateTime:
        return DateTime(datetime.now(_system_timezone()), format)


def now() -> datetime:
    return datetime.now(_system_timezone())


def parse_datetime(value: str) -> datetime:
    try:
        return aniso8601.parse_datetime(value)
    except ValueError:
        raise ValueError(f'An invalid datetime format: {value}')


def _system_timezone() -> timezone:
    localtime = time.localtime()
    return timezone(
        offset=timedelta(seconds=localtime.tm_gmtoff),
        name=localtime.tm_zone,
    )
