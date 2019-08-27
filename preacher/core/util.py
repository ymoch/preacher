"""Utilities for Preacher Core."""

import datetime
import time


def now() -> datetime.datetime:
    return datetime.datetime.now(_system_timezone())


def _system_timezone() -> datetime.timezone:
    localtime = time.localtime()
    return datetime.timezone(
        offset=datetime.timedelta(seconds=localtime.tm_gmtoff),
        name=localtime.tm_zone,
    )
