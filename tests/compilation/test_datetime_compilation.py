from datetime import time, timedelta, timezone
from unittest.mock import sentinel

from pytest import mark, raises

from preacher.compilation.datetime import compile_datetime_format
from preacher.compilation.datetime import compile_time
from preacher.compilation.datetime import compile_timedelta
from preacher.compilation.error import CompilationError
from preacher.core.datetime import ISO8601

PKG = 'preacher.compilation.datetime'


@mark.parametrize('obj', (1, 1.2, complex(1, 2), [], {}))
def test_compile_datetime_format_given_invalid(obj):
    with raises(CompilationError):
        compile_datetime_format(obj)


@mark.parametrize('obj', (None, 'iso8601', 'ISO8601', 'iSo8601'))
def test_compile_datetime_format_iso8601(obj):
    assert compile_datetime_format(obj) is ISO8601


@mark.parametrize('obj', ('', '%Y-%m-%s', 'xxx'))
def test_compile_datetime_format_strftime(mocker, obj):
    ctor = mocker.patch(f'{PKG}.StrftimeFormat', return_value=sentinel.result)

    assert compile_datetime_format(obj) is sentinel.result
    ctor.assert_called_once_with(obj)


@mark.parametrize('obj', (None, 1, [], {}, 'invalid', 'now', '1', '1:2', '1:2:3'))
def test_compile_time_given_an_invalid_format(obj):
    # HACK delegate tests.
    with raises(CompilationError):
        compile_time(obj)


@mark.parametrize(('obj', 'expected'), (
    ('01', time(hour=1, tzinfo=timezone.utc)),
    ('01+09:00', time(hour=1, tzinfo=timezone(timedelta(hours=9)))),
    ('01:02', time(hour=1, minute=2, tzinfo=timezone.utc)),
    ('01:02+09:00', time(hour=1, minute=2, tzinfo=timezone(timedelta(hours=9)))),
    ('01:02:03', time(hour=1, minute=2, second=3, tzinfo=timezone.utc)),
    ('01:02:03.012', time(hour=1, minute=2, second=3, microsecond=12000, tzinfo=timezone.utc)),
    ('01:02:03.012345', time(hour=1, minute=2, second=3, microsecond=12345, tzinfo=timezone.utc)),
))
def test_compile_time(mocker, obj, expected):
    # HACK delegate tests.
    mocker.patch('preacher.core.datetime.system_timezone', return_value=timezone.utc)
    assert compile_time(obj) == expected


@mark.parametrize('obj', (None, 1, [], {}, 'invalid', 'now +1 day'))
def test_compile_timedelta_given_an_invalid_format(obj):
    with raises(CompilationError):
        compile_timedelta(obj)


@mark.parametrize(('obj', 'expected'), (
    ('', timedelta()),
    ('now', timedelta()),
    (' now ', timedelta()),
    ('0day', timedelta()),
    ('1day', timedelta(days=1)),
    ('2 DaYs', timedelta(days=2)),
    ('+365 days', timedelta(days=365)),
    (' -1  days ', timedelta(days=-1)),
    ('0 hour', timedelta()),
    ('1 hour', timedelta(hours=1)),
    ('-2 hours', timedelta(hours=-2)),
    ('24 hours', timedelta(days=1)),
    ('-48 hours', timedelta(days=-2)),
    ('0 minute', timedelta()),
    ('1 minute', timedelta(minutes=1)),
    ('-2 minutes', timedelta(minutes=-2)),
    ('+60 minutes', timedelta(hours=1)),
    ('-120 minutes', timedelta(hours=-2)),
    ('0 second', timedelta()),
    ('1 seconds', timedelta(seconds=1)),
    ('-2 seconds', timedelta(seconds=-2)),
    ('+60 seconds', timedelta(minutes=1)),
    ('-120 seconds', timedelta(minutes=-2)),
))
def test_compile_timedelta(obj, expected):
    assert compile_timedelta(obj) == expected
