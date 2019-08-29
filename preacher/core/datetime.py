"""Datetime utilities for Preacher core."""

import datetime
import time


def now() -> datetime.datetime:
    return datetime.datetime.now(_system_timezone())


def parse_datetime(value: str) -> datetime.datetime:
    """
    Only takes ISO 6801 expanded format.
    """
    if value.endswith('Z'):
        value = value[:-1] + '+00:00'
    return datetime.datetime.fromisoformat(value)


def _system_timezone() -> datetime.timezone:
    localtime = time.localtime()
    return datetime.timezone(
        offset=datetime.timedelta(seconds=localtime.tm_gmtoff),
        name=localtime.tm_zone,
    )
