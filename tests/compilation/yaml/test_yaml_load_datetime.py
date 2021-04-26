from datetime import datetime, timezone, timedelta
from io import StringIO

from pytest import mark, raises

from preacher.compilation.yaml import YamlError, load
from preacher.core.value import ValueContext
from preacher.core.value.impl.datetime import RelativeDatetime


def test_given_datetime_that_is_offset_naive():
    stream = StringIO('2020-04-01 01:23:45')
    actual = load(stream)
    assert isinstance(actual, datetime)
    assert actual == datetime(2020, 4, 1, 1, 23, 45)
    assert actual.tzinfo is None


def test_given_datetime_that_is_offset_aware():
    stream = StringIO('2020-04-01 01:23:45 +09:00')
    actual = load(stream)
    assert isinstance(actual, datetime)
    assert (
        actual - datetime(2020, 3, 31, 16, 23, 45, tzinfo=timezone.utc)
    ).total_seconds() == 0.0
    assert actual.tzinfo


@mark.parametrize(('content', 'expected_message'), [
    ('!relative_datetime []', '", line 1, column 1'),
    ('\n- !relative_datetime invalid', '", line 2, column 3'),
    ('!relative_datetime {delta: invalid}', '", line 1, column 28'),
    ('!relative_datetime {format: {}}', '", line 1, column 29')
])
def test_given_invalid_relative_datetime(content, expected_message):
    stream = StringIO(content)
    with raises(YamlError) as error_info:
        load(stream)
    assert expected_message in str(error_info.value)


def test_given_an_empty_relative_datetime():
    actual = load(StringIO('!relative_datetime'))
    assert isinstance(actual, RelativeDatetime)

    now = datetime.now()
    resolved = actual.resolve(ValueContext(origin_datetime=now))
    assert resolved.value == now


def test_given_a_valid_string_relative_datetime():
    actual = load(StringIO('!relative_datetime -1 hour'))
    assert isinstance(actual, RelativeDatetime)

    now = datetime.now()
    resolved = actual.resolve(ValueContext(origin_datetime=now))
    assert resolved.value == now - timedelta(hours=1)


def test_given_an_empty_mapping_relative_datetime():
    actual = load(StringIO('!relative_datetime {}'))
    assert isinstance(actual, RelativeDatetime)

    now = datetime.now()
    resolved = actual.resolve(ValueContext(origin_datetime=now))
    assert resolved.value == now


def test_given_a_filled_mapping_relative_datetime():
    content = '\n'.join([
        '!relative_datetime',
        '  delta: -1 minute',
        '  format: "%H:%M:%S"',
        '  foo: bar',  # Invalid one will be ignored.
    ])
    actual = load(StringIO(content))
    assert isinstance(actual, RelativeDatetime)

    now = datetime(2020, 1, 23, 12, 34, 56)
    resolved = actual.resolve(ValueContext(origin_datetime=now))
    assert resolved.formatted == '12:33:56'
