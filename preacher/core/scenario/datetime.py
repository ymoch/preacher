"""
Datetime utilities for Preacher core.
"""

import datetime
import time

import aniso8601


def now() -> datetime.datetime:
    return datetime.datetime.now(_system_timezone())


def parse_datetime(value: str) -> datetime.datetime:
    try:
        return aniso8601.parse_datetime(value)
    except ValueError:
        raise ValueError(f'An invalid datetime format: {value}')


def _system_timezone() -> datetime.timezone:
    localtime = time.localtime()
    return datetime.timezone(
        offset=datetime.timedelta(seconds=localtime.tm_gmtoff),
        name=localtime.tm_zone,
    )
