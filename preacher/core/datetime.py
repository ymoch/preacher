"""
Datetime utilities for Preacher core.
"""

import time
from abc import ABC
from datetime import datetime, timedelta, timezone
from typing import Optional

from dateutil.parser import isoparse


class DatetimeFormat(ABC):

    def format_datetime(self, value: datetime) -> str:
        raise NotImplementedError()

    def parse_datetime(self, value: str) -> datetime:
        raise NotImplementedError()


class Iso8601Format(DatetimeFormat):

    def format_datetime(self, value: datetime) -> str:
        return value.isoformat()

    def parse_datetime(self, value: str) -> datetime:
        try:
            return isoparse(value)
        except ValueError as error:
            raise ValueError(f'An invalid ISO 8601 format: {value}', error)


class StrftimeFormat(DatetimeFormat):

    def __init__(self, format_string: str):
        self._format_string = format_string

    def format_datetime(self, value: datetime) -> str:
        return value.strftime(self._format_string)

    def parse_datetime(self, value: str) -> datetime:
        return datetime.strptime(value, self._format_string)


ISO8601 = Iso8601Format()


class DatetimeWithFormat:

    def __init__(
        self,
        value: datetime,
        fmt: Optional[DatetimeFormat] = None,
    ):
        self._value = value
        self._fmt = fmt or ISO8601

    @property
    def value(self) -> datetime:
        return self._value

    @property
    def fmt(self) -> DatetimeFormat:
        return self._fmt

    @property
    def formatted(self) -> str:
        return self._fmt.format_datetime(self._value)


def now() -> datetime:
    """Returns the current datetime in the system timezone."""
    return datetime.now(system_timezone())


def system_timezone() -> timezone:
    """Returns the system timezone."""
    localtime = time.localtime()
    return timezone(
        offset=timedelta(seconds=localtime.tm_gmtoff),
        name=localtime.tm_zone,
    )
