from datetime import datetime, timezone

from hamcrest.core.string_description import StringDescription
from pytest import mark, raises

from preacher.core.hamcrest import after, before

ORIGIN = datetime(2019, 12, 15, 12, 34, 56, tzinfo=timezone.utc)


@mark.parametrize('value', [
    None,
    1,
    1.2,
    complex(1, 2),
    'str',
])
def test_before_invalid_creation(value):
    with raises(TypeError):
        before(value)


@mark.parametrize('item', [None, 1])
def test_after_invalid_validation(item):
    matcher = after(ORIGIN)
    with raises(TypeError):
        matcher.matches(item)


@mark.parametrize(('item', 'expected'), [
    ('2019-12-15T12:34:55Z', True),
    ('2019-12-15T12:34:56Z', False),
    ('2019-12-15T12:34:57Z', False),
])
def test_before(item, expected):
    matcher = before(ORIGIN)
    assert matcher.matches(item) == expected

    description = StringDescription()
    matcher.describe_to(description)
    assert str(description).startswith('a value before <2019-12')

    description = StringDescription()
    matcher.describe_mismatch(item, description)
    assert str(description).startswith('was <2019-12')


@mark.parametrize('item, expected', [
    ('2019-12-15T12:34:55Z', False),
    ('2019-12-15T12:34:56Z', False),
    ('2019-12-15T12:34:57Z', True),
])
def test_after(item, expected):
    matcher = after(ORIGIN)
    assert matcher.matches(item) == expected

    description = StringDescription()
    matcher.describe_to(description)
    assert str(description).startswith('a value after <2019-12')

    description = StringDescription()
    matcher.describe_mismatch(item, description)
    assert str(description).startswith('was <2019-12')
