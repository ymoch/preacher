import time
from datetime import datetime, timezone
from unittest.mock import NonCallableMock

from pytest import mark, raises

from preacher.core.datetime import DateTimeFormat, ISO8601, now, parse_datetime


def test_date_time_format_interface():
    class _Incomplete(DateTimeFormat):
        def format_datetime(self, value: datetime) -> str:
            return super().format_datetime(value)

        def parse_datetime(self, value: str) -> datetime:
            return super().parse_datetime(value)

    format = _Incomplete()
    with raises(NotImplementedError):
        format.parse_datetime('str')
    with raises(NotImplementedError):
        format.format_datetime(datetime.now())


@mark.parametrize(('value', 'expected'), [
    (
        datetime(2345, 12, 31, 23, 59, 59),
        '2345-12-31T23:59:59',
    ),
    (
        datetime(2345, 12, 31, 23, 59, 59, 123456, tzinfo=timezone.utc),
        '2345-12-31T23:59:59.123456+00:00',
    ),
])
def test_iso8601_format_datetime(value, expected):
    assert ISO8601.format_datetime(value) == expected


@mark.parametrize(('value', 'expected'), [
    (
        '1234-01-23T01:23:45',
        datetime(1234, 1, 23, 1, 23, 45),
    ),
    (
        '1234-01-23T01:23:45.123456Z',
        datetime(1234, 1, 23, 1, 23, 45, 123456, tzinfo=timezone.utc),
    ),
])
def test_iso8601_parse_datetime(value, expected):
    assert ISO8601.parse_datetime(value) == expected


def test_now_jst(mocker):
    localtime = NonCallableMock(
        spec=time.struct_time,
        tm_zone='JST',
        tm_gmtoff=32400,
    )
    mocker.patch('time.localtime', return_value=localtime)

    current = now()
    assert current.tzname() == 'JST'
    assert current.utcoffset().total_seconds() == 32400


def test_now_pdt(mocker):
    localtime = NonCallableMock(
        spec=time.struct_time,
        tm_zone='PDT',
        tm_gmtoff=-28800,
    )
    mocker.patch('time.localtime', return_value=localtime)

    current = now()
    assert current.tzname() == 'PDT'
    assert current.utcoffset().total_seconds() == -28800


@mark.parametrize('value', [
    '',
    'XXX',
    'XXXTYYY',
])
def test_parse_date_given_invalid_format(value):
    with raises(ValueError):
        parse_datetime('value')


def test_parse_datetime_given_iso_8601_format_ends_with_z():
    dt = parse_datetime('20190828T024543.477Z')
    assert dt.year == 2019
    assert dt.month == 8
    assert dt.day == 28
    assert dt.hour == 2
    assert dt.minute == 45
    assert dt.second == 43
    assert dt.microsecond == 477000
    assert dt.utcoffset().total_seconds() == 0


def test_parse_datetime_given_iso_8601_expanded_format():
    dt = parse_datetime('2019-08-28T02:45:43,477123-09:00')
    assert dt.year == 2019
    assert dt.month == 8
    assert dt.day == 28
    assert dt.hour == 2
    assert dt.minute == 45
    assert dt.second == 43
    assert dt.microsecond == 477123
    assert dt.utcoffset().total_seconds() == -9 * 60 * 60
