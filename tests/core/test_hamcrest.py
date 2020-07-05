from datetime import datetime, timezone

from hamcrest.core.string_description import StringDescription
from pytest import mark, raises

from preacher.core.datetime import DatetimeWithFormat
from preacher.core.hamcrest import after, before

ORIGIN = datetime(2019, 12, 15, 12, 34, 56, tzinfo=timezone.utc)


@mark.parametrize('value', [
    None,
    1,
    1.2,
    complex(1, 2),
    'str',
])
def test_datetime_matcher_invalid_creation(value):
    with raises(TypeError):
        before(value)
    with raises(TypeError):
        after(value)


@mark.parametrize('item', [None, 1])
def test_datetime_matcher_invalid_validation(item):
    matcher = before(ORIGIN)
    with raises(TypeError):
        matcher.matches(item)

    matcher = after(ORIGIN)
    with raises(TypeError):
        matcher.matches(item)


@mark.parametrize(('value', 'item', 'before_expected', 'after_expected'), [
    (ORIGIN, '2019-12-15T12:34:55Z', True, False),
    (ORIGIN, '2019-12-15T12:34:56Z', False, False),
    (ORIGIN, '2019-12-15T12:34:57Z', False, True),
    (DatetimeWithFormat(ORIGIN), '2019-12-15T12:34:55Z', True, False),
    (DatetimeWithFormat(ORIGIN), '2019-12-15T12:34:56Z', False, False),
    (DatetimeWithFormat(ORIGIN), '2019-12-15T12:34:57Z', False, True),
])
def test_datetime_matcher(value, item, before_expected, after_expected):
    matcher = before(ORIGIN)
    assert matcher.matches(item) == before_expected
    description = StringDescription()
    matcher.describe_to(description)
    assert str(description).startswith('a value before <')
    description = StringDescription()
    matcher.describe_mismatch(item, description)
    assert str(description).startswith('was <')

    matcher = after(value)
    assert matcher.matches(item) == after_expected
    description = StringDescription()
    matcher.describe_to(description)
    assert str(description).startswith('a value after <')
    description = StringDescription()
    matcher.describe_mismatch(item, description)
    assert str(description).startswith('was <')
