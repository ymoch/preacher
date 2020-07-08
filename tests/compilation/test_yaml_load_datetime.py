from datetime import datetime, timezone, timedelta
from io import StringIO

from pytest import mark, raises

from preacher.compilation import CompilationError
from preacher.compilation.yaml import load
from preacher.core.interpretation import RelativeDatetime, ValueContext


def test_given_datetime_that_is_offset_naive():
    io = StringIO('2020-04-01 01:23:45')
    actual = load(io)
    assert isinstance(actual, datetime)
    assert actual == datetime(2020, 4, 1, 1, 23, 45)
    assert actual.tzinfo is None


def test_given_datetime_that_is_offset_aware():
    io = StringIO('2020-04-01 01:23:45 +09:00')
    actual = load(io)
    assert isinstance(actual, datetime)
    assert (
        actual - datetime(2020, 3, 31, 16, 23, 45, tzinfo=timezone.utc)
    ).total_seconds() == 0.0
    assert actual.tzinfo


@mark.parametrize('content', [
    '!relative_datetime []',
    '!relative_datetime {}',
    '!relative_datetime invalid',
])
def test_given_invalid_relative_datetime(content):
    io = StringIO(content)
    with raises(CompilationError):
        load(io)


def test_given_a_valid_relative_datetime():
    io = StringIO('!relative_datetime -1 hour')
    actual = load(io)
    assert isinstance(actual, RelativeDatetime)

    now = datetime.now()
    resolved = actual.resolve(ValueContext(origin_datetime=now))
    assert resolved.value == now - timedelta(hours=1)


def test_given_a_valid_full_relative_datetime():
    io = StringIO('!relative_datetime {delta: -1 minute, format: "%H:%M:%S"}')
    actual = load(io)
    assert isinstance(actual, RelativeDatetime)

    now = datetime(2020, 1, 23, 12, 34, 56)
    resolved = actual.resolve(ValueContext(origin_datetime=now))
    assert resolved.formatted == '12:33:56'
