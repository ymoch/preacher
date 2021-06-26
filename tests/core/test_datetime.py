from time import struct_time
from datetime import datetime, time, timedelta, timezone
from unittest.mock import NonCallableMock

from pytest import mark, raises

from preacher.core.datetime import DatetimeFormat
from preacher.core.datetime import StrftimeFormat
from preacher.core.datetime import ISO8601
from preacher.core.datetime import now
from preacher.core.datetime import parse_time
from preacher.core.datetime import parse_timedelta

PKG = "preacher.core.datetime"


def test_date_time_format_interface():
    class _Incomplete(DatetimeFormat):
        def format_datetime(self, value: datetime) -> str:
            return super().format_datetime(value)

        def parse_datetime(self, value: str) -> datetime:
            return super().parse_datetime(value)

    format = _Incomplete()
    with raises(NotImplementedError):
        format.parse_datetime("str")
    with raises(NotImplementedError):
        format.format_datetime(datetime.now())


@mark.parametrize(
    ("value", "expected"),
    (
        (datetime(2345, 12, 31), "2345-12-31T00:00:00"),
        (datetime(2345, 12, 31, 23, 59, 59), "2345-12-31T23:59:59"),
        (
            datetime(2345, 12, 31, 23, 59, 59, 123456, tzinfo=timezone.utc),
            "2345-12-31T23:59:59.123456+00:00",
        ),
    ),
)
def test_iso8601_format_datetime(value, expected):
    assert ISO8601.format_datetime(value) == expected


@mark.parametrize(
    "value",
    (
        "",
        "XXX",
        "XXXTYYY",
        "2019-01-23T",
        "20190123T",
    ),
)
def test_iso8601_format_datetime_invalid(value):
    with raises(ValueError):
        ISO8601.parse_datetime(value)


@mark.parametrize(
    ("value", "expected"),
    (
        ("20190123", datetime(2019, 1, 23)),
        ("2019-01-23", datetime(2019, 1, 23)),
        ("1234-01-23T01:23:45", datetime(1234, 1, 23, 1, 23, 45)),
        (
            "20190828T024543.477Z",
            datetime(2019, 8, 28, 2, 45, 43, 477000, timezone.utc),
        ),
        (
            "1234-01-23T01:23:45.123456Z",
            datetime(1234, 1, 23, 1, 23, 45, 123456, timezone.utc),
        ),
        (
            "2019-08-09T02:45:43,477123-09:00",
            datetime(2019, 8, 9, 2, 45, 43, 477123, timezone(timedelta(hours=-9))),
        ),
    ),
)
def test_iso8601_parse_datetime(value, expected):
    assert ISO8601.parse_datetime(value) == expected


@mark.parametrize(
    ("format_string", "value", "expected"),
    (
        ("%Y-%m-%d", datetime(1234, 1, 1), "1234-01-01"),
        (
            "%Y-%m-%d %H:%M:%S %Z",
            datetime(1234, 1, 1, tzinfo=timezone.utc),
            "1234-01-01 00:00:00 UTC",
        ),
    ),
)
def test_strftime_format_datetime(format_string, value, expected):
    assert StrftimeFormat(format_string).format_datetime(value) == expected


@mark.parametrize(
    ("format_string", "value", "expected"),
    (
        ("%Y-%m-%d", "1234-01-01", datetime(1234, 1, 1)),
        (
            "%Y-%m-%d %H:%M:%S %z",
            "1234-01-01 00:00:00 -09:00",
            datetime(1234, 1, 1, tzinfo=timezone(timedelta(hours=-9))),
        ),
    ),
)
def test_strftime_parse_datetime(format_string, value, expected):
    assert StrftimeFormat(format_string).parse_datetime(value) == expected


def test_now_jst(mocker):
    localtime = NonCallableMock(spec=struct_time, tm_zone="JST", tm_gmtoff=32400)
    mocker.patch(f"{PKG}.localtime", return_value=localtime)

    current = now()
    assert current.tzname() == "JST"
    assert current.utcoffset().total_seconds() == 32400


def test_now_pdt(mocker):
    localtime = NonCallableMock(spec=struct_time, tm_zone="PDT", tm_gmtoff=-28800)
    mocker.patch(f"{PKG}.localtime", return_value=localtime)

    current = now()
    assert current.tzname() == "PDT"
    assert current.utcoffset().total_seconds() == -28800


@mark.parametrize("value", ("invalid", "now", "1", "1:2", "1:2:3"))
def test_parse_time_given_an_invalid_value(value):
    with raises(ValueError):
        parse_time(value)


@mark.parametrize(
    ("value", "expected"),
    (
        ("01", time(hour=1, tzinfo=timezone.utc)),
        ("01+09:00", time(hour=1, tzinfo=timezone(timedelta(hours=9)))),
        ("01:02", time(hour=1, minute=2, tzinfo=timezone.utc)),
        ("01:02+09:00", time(hour=1, minute=2, tzinfo=timezone(timedelta(hours=9)))),
        ("01:02:03", time(hour=1, minute=2, second=3, tzinfo=timezone.utc)),
        ("01:02:03.012", time(hour=1, minute=2, second=3, microsecond=12000, tzinfo=timezone.utc)),
        (
            "01:02:03.012345",
            time(hour=1, minute=2, second=3, microsecond=12345, tzinfo=timezone.utc),
        ),
    ),
)
def test_parse_time(mocker, value, expected):
    mocker.patch(f"{PKG}.system_timezone", return_value=timezone.utc)
    assert parse_time(value) == expected


@mark.parametrize("value", ("invalid", "now +1 day"))
def test_parse_timedelta_given_an_invalid_value(value):
    with raises(ValueError):
        parse_timedelta(value)


@mark.parametrize(
    ("value", "expected"),
    (
        ("", timedelta()),
        ("now", timedelta()),
        (" now ", timedelta()),
        ("0day", timedelta()),
        ("1day", timedelta(days=1)),
        ("2 DaYs", timedelta(days=2)),
        ("+365 days", timedelta(days=365)),
        (" -1  days ", timedelta(days=-1)),
        ("0 hour", timedelta()),
        ("1 hour", timedelta(hours=1)),
        ("-2 hours", timedelta(hours=-2)),
        ("24 hours", timedelta(days=1)),
        ("-48 hours", timedelta(days=-2)),
        ("0 minute", timedelta()),
        ("1 minute", timedelta(minutes=1)),
        ("-2 minutes", timedelta(minutes=-2)),
        ("+60 minutes", timedelta(hours=1)),
        ("-120 minutes", timedelta(hours=-2)),
        ("0 second", timedelta()),
        ("1 seconds", timedelta(seconds=1)),
        ("-2 seconds", timedelta(seconds=-2)),
        ("+60 seconds", timedelta(minutes=1)),
        ("-120 seconds", timedelta(minutes=-2)),
    ),
)
def test_parse_timedelta(value, expected):
    assert parse_timedelta(value) == expected
