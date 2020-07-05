"""
Datetime utilities for Preacher core.
"""
from __future__ import annotations

from abc import ABC
from datetime import datetime, timedelta, timezone
import time
from typing import Optional

import aniso8601


class DateTimeFormat(ABC):

    def format_datetime(self, value: datetime) -> str:
        raise NotImplementedError()

    def parse_datetime(self, value: str) -> datetime:
        raise NotImplementedError()


class Iso8601Format(DateTimeFormat):

    def format_datetime(self, value: datetime) -> str:
        return value.isoformat()

    def parse_datetime(self, value: str) -> datetime:
        try:
            return aniso8601.parse_datetime(value)
        except ValueError:
            raise ValueError(f'An invalid datetime format: {value}')


ISO8601 = Iso8601Format()


class DateTimeWithFormat:

    def __init__(
        self,
        value: datetime,
        fmt: Optional[DateTimeFormat] = None,
    ):
        self._value = value
        self._fmt = fmt or ISO8601

    @property
    def value(self) -> datetime:
        return self._value

    @property
    def fmt(self) -> DateTimeFormat:
        return self._fmt

    @property
    def formatted(self) -> str:
        return self._fmt.format_datetime(self._value)


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
