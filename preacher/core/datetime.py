"""
Datetime utilities for Preacher core.
"""
from __future__ import annotations

from abc import ABC
from datetime import datetime, timedelta, timezone
import time
from typing import Optional

import aniso8601


class DateTimeFormatter(ABC):

    def format_datetime(self, value: datetime) -> str:
        raise NotImplementedError()

    def parse_datetime(self, value: str) -> datetime:
        raise NotImplementedError()


class Iso8601Formatter(DateTimeFormatter):

    def format_datetime(self, value: datetime) -> str:
        return value.isoformat()

    def parse_datetime(self, value: str) -> datetime:
        return aniso8601.parse_datetime(value)


ISO8601 = Iso8601Formatter()


class DateTime:

    def __init__(
        self,
        value: datetime,
        formatter: Optional[DateTimeFormatter] = None,
    ):
        self._value = value
        self._formatter = formatter or ISO8601

    @property
    def value(self) -> datetime:
        return self._value

    @property
    def formatter(self) -> DateTimeFormatter:
        return self._formatter

    @property
    def formatted(self) -> str:
        return self._formatter.format_datetime(self._value)

    @staticmethod
    def now(formatter: Optional[DateTimeFormatter] = None) -> DateTime:
        return DateTime(datetime.now(_system_timezone()), formatter)


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
