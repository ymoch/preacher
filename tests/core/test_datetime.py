import time
from unittest.mock import MagicMock, patch

from pytest import raises

from preacher.core.datetime import now, parse_datetime


@patch('time.localtime')
def test_now_jst(localtime):
    localtime.return_value = MagicMock(
        spec=time.struct_time,
        tm_zone='JST',
        tm_gmtoff=32400,
    )
    current = now()
    assert current.tzname() == 'JST'
    assert current.utcoffset().total_seconds() == 32400


@patch('time.localtime')
def test_now_pdt(localtime):
    localtime.return_value = MagicMock(
        spec=time.struct_time,
        tm_zone='PDT',
        tm_gmtoff=-28800,
    )
    current = now()
    assert current.tzname() == 'PDT'
    assert current.utcoffset().total_seconds() == -28800


def test_parse_date_given_invalid_format():
    with raises(ValueError) as error_info:
        parse_datetime('XXX')
    assert 'XXX' in str(error_info.value)


def test_parse_datetime_given_iso_expanded_format():
    dt = parse_datetime('2019-08-28T02:45:43.477123-09:00')
    assert dt.year == 2019
    assert dt.month == 8
    assert dt.day == 28
    assert dt.hour == 2
    assert dt.minute == 45
    assert dt.second == 43
    assert dt.microsecond == 477123
    assert dt.utcoffset().total_seconds() == -9 * 60 * 60


def test_parse_datetime_given_iso_expanded_format_ends_with_z():
    dt = parse_datetime('2019-08-28T02:45:43.477Z')
    assert dt.year == 2019
    assert dt.month == 8
    assert dt.day == 28
    assert dt.hour == 2
    assert dt.minute == 45
    assert dt.second == 43
    assert dt.microsecond == 477000
    assert dt.utcoffset().total_seconds() == 0
