from datetime import datetime, timezone

from hamcrest.core.string_description import StringDescription
from pytest import mark

from preacher.core.hamcrest import after, before

ORIGIN = datetime(2019, 12, 31, 12, 34, 56, tzinfo=timezone.utc)


@mark.parametrize('item, expected', [
    ('2019-12-31T12:34:55Z', True),
    ('2019-12-31T12:34:56Z', False),
    ('2019-12-31T12:34:57Z', False),
])
def test_before(item, expected):
    matcher = before(ORIGIN)
    assert matcher.matches(item) == expected

    description = StringDescription()
    matcher.describe_to(description)
    assert str(description).startswith('a value less than')


@mark.parametrize('item, expected', [
    ('2019-12-31T12:34:55Z', False),
    ('2019-12-31T12:34:56Z', False),
    ('2019-12-31T12:34:57Z', True),
])
def test_after(item, expected):
    matcher = after(ORIGIN)
    assert matcher.matches(item) == expected

    description = StringDescription()
    matcher.describe_to(description)
    assert str(description).startswith('a value greater than')
