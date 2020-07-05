from datetime import timedelta
from unittest.mock import sentinel

from pytest import mark, raises

from preacher.compilation.datetime import (
    compile_datetime_format,
    compile_timedelta,
)
from preacher.compilation.error import CompilationError
from preacher.core.datetime import ISO8601

PKG = 'preacher.compilation.datetime'


@mark.parametrize('obj', [
    1,
    1.2,
    complex(1, 2),
    [],
    {},
])
def test_compile_datetime_format_given_invalid(obj):
    with raises(CompilationError):
        compile_datetime_format(obj)


@mark.parametrize('obj', [
    None,
    'iso8601',
    'ISO8601',
    'iSo8601',
])
def test_compile_datetime_format_iso8601(obj):
    assert compile_datetime_format(obj) is ISO8601


@mark.parametrize('obj', [
    '',
    '%Y-%m-%s',
    'xxx',
])
def test_compile_datetime_format_strftime(mocker, obj):
    ctor = mocker.patch(f'{PKG}.StrftimeFormat', return_value=sentinel.result)

    assert compile_datetime_format(obj) is sentinel.result
    ctor.assert_called_once_with(obj)


@mark.parametrize('value', (
    None,
    1,
    [],
    {},
    'invalid',
    'now +1 day',
))
def test_compile_timedelta_given_an_invalid_format(value):
    with raises(CompilationError):
        compile_timedelta(value)


@mark.parametrize('value, expected', (
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
def test_compile_timedelta(value, expected):
    actual = compile_timedelta(value)
    assert actual == expected
