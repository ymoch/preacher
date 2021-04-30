import time
from datetime import datetime, timedelta, timezone
from unittest.mock import NonCallableMock

from pytest import mark, raises

from preacher.core.datetime import DatetimeFormat, ISO8601, StrftimeFormat, now

PKG = 'preacher.core.datetime'


def test_date_time_format_interface():
    class _Incomplete(DatetimeFormat):
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
    (datetime(2345, 12, 31), '2345-12-31T00:00:00'),
    (datetime(2345, 12, 31, 23, 59, 59), '2345-12-31T23:59:59'),
    (
        datetime(2345, 12, 31, 23, 59, 59, 123456, tzinfo=timezone.utc),
        '2345-12-31T23:59:59.123456+00:00',
    ),
])
def test_iso8601_format_datetime(value, expected):
    assert ISO8601.format_datetime(value) == expected


@mark.parametrize('value', [
    '',
    'XXX',
    'XXXTYYY',
    '2019-01-23T',
    '20190123T',
])
def test_iso8601_format_datetime_invalid(value):
    with raises(ValueError):
        ISO8601.parse_datetime(value)


@mark.parametrize(('value', 'expected'), [
    ('20190123', datetime(2019, 1, 23)),
    ('2019-01-23', datetime(2019, 1, 23)),
    ('1234-01-23T01:23:45', datetime(1234, 1, 23, 1, 23, 45)),
    (
        '20190828T024543.477Z',
        datetime(2019, 8, 28, 2, 45, 43, 477000, timezone.utc),
    ),
    (
        '1234-01-23T01:23:45.123456Z',
        datetime(1234, 1, 23, 1, 23, 45, 123456, timezone.utc),
    ),
    (
        '2019-08-09T02:45:43,477123-09:00',
        datetime(2019, 8, 9, 2, 45, 43, 477123, timezone(timedelta(hours=-9))),
    ),
])
def test_iso8601_parse_datetime(value, expected):
    assert ISO8601.parse_datetime(value) == expected


@mark.parametrize(('format_string', 'value', 'expected'), [
    ('%Y-%m-%d', datetime(1234, 1, 1), '1234-01-01'),
    (
        '%Y-%m-%d %H:%M:%S %Z',
        datetime(1234, 1, 1, tzinfo=timezone.utc),
        '1234-01-01 00:00:00 UTC',
    )
])
def test_strftime_format_datetime(format_string, value, expected):
    assert StrftimeFormat(format_string).format_datetime(value) == expected


@mark.parametrize(('format_string', 'value', 'expected'), [
    ('%Y-%m-%d', '1234-01-01', datetime(1234, 1, 1)),
    (
        '%Y-%m-%d %H:%M:%S %z',
        '1234-01-01 00:00:00 -09:00',
        datetime(1234, 1, 1, tzinfo=timezone(timedelta(hours=-9))),
    )
])
def test_strftime_parse_datetime(format_string, value, expected):
    assert StrftimeFormat(format_string).parse_datetime(value) == expected


def test_now_jst(mocker):
    localtime = NonCallableMock(spec=time.struct_time, tm_zone='JST', tm_gmtoff=32400)
    mocker.patch(f'{PKG}.localtime', return_value=localtime)

    current = now()
    assert current.tzname() == 'JST'
    assert current.utcoffset().total_seconds() == 32400


def test_now_pdt(mocker):
    localtime = NonCallableMock(spec=time.struct_time, tm_zone='PDT', tm_gmtoff=-28800)
    mocker.patch(f'{PKG}.localtime', return_value=localtime)

    current = now()
    assert current.tzname() == 'PDT'
    assert current.utcoffset().total_seconds() == -28800
