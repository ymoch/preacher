from datetime import datetime

from pytest import mark, raises

from preacher.compilation.util import compile_datetime


ORIGIN = datetime(2019, 8, 28)


def test_compile_datetime_given_an_invalid_format():
    with raises(ValueError):
        compile_datetime('invalid')


@mark.parametrize('value, expected', (
    ('0day', '2019-08-28'),
    ('1day', '2019-08-29'),
    ('4 DaYs', '2019-09-01'),
    ('365 days', '2020-08-27'),
    (' -1  days ', '2019-08-27'),
))
def test_compile_datetime_given_a_relative_day(value, expected):
    actual = compile_datetime(value, origin=ORIGIN)
    assert f'{actual:%Y-%m-%d}' == expected


@mark.parametrize('value, expected', (
    ('0 hour', '2019-08-28 00:00:00'),
    ('1 hour', '2019-08-28 01:00:00'),
    ('-2 hours', '2019-08-27 22:00:00'),
    ('24 hours', '2019-08-29 00:00:00'),
    ('-48 hours', '2019-08-26 00:00:00'),
))
def test_compile_datetime_given_a_relative_hour(value, expected):
    actual = compile_datetime(value, origin=ORIGIN)
    assert f'{actual:%Y-%m-%d %H:%M:%S}' == expected


@mark.parametrize('value, expected', (
    ('0 minute', '2019-08-28 00:00:00'),
    ('1 minute', '2019-08-28 00:01:00'),
    ('-2 minutes', '2019-08-27 23:58:00'),
    ('+60 minutes', '2019-08-28 01:00:00'),
    ('-120 minutes', '2019-08-27 22:00:00'),
))
def test_compile_datetime_given_a_relative_minute(value, expected):
    actual = compile_datetime(value, origin=ORIGIN)
    assert f'{actual:%Y-%m-%d %H:%M:%S}' == expected


@mark.parametrize('value, expected', (
    ('0 second', '2019-08-28 00:00:00'),
    ('1 seconds', '2019-08-28 00:00:01'),
    ('-2 seconds', '2019-08-27 23:59:58'),
    ('+60 seconds', '2019-08-28 00:01:00'),
    ('-120 seconds', '2019-08-27 23:58:00'),
))
def test_compile_datetime_given_a_relative_seconds(value, expected):
    actual = compile_datetime(value, origin=ORIGIN)
    assert f'{actual:%Y-%m-%d %H:%M:%S}' == expected
