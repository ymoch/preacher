"""
Datetime utilities for Preacher core.
"""
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
        except (ValueError, IndexError):  # Raises IndexError for '12345678T'
            raise ValueError(f'An invalid datetime format: {value}')


class StrftimeFormat(DateTimeFormat):

    def __init__(self, format_string: str):
        self._format_string = format_string

    def format_datetime(self, value: datetime) -> str:
        return value.strftime(self._format_string)

    def parse_datetime(self, value: str) -> datetime:
        return datetime.strptime(value, self._format_string)


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


def _system_timezone() -> timezone:
    localtime = time.localtime()
    return timezone(
        offset=timedelta(seconds=localtime.tm_gmtoff),
        name=localtime.tm_zone,
    )
