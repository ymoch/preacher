from datetime import timedelta

from pytest import mark

from preacher.compilation.error import CompilationError
from preacher.compilation.datetime import compile_relative_datetime


@mark.xfail(raises=CompilationError)
def test_compile_datetime_given_an_invalid_format():
    compile_relative_datetime('invalid')


@mark.parametrize('value, expected', (
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
def test_compile_relative_datetime(value, expected):
    actual = compile_relative_datetime(value)
    assert actual == expected
