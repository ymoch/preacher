from datetime import date, datetime

from pytest import mark

from preacher.core.scenario.type import is_scalar


@mark.parametrize('value, expected', [
    (None, False),
    (False, True),
    (0, True),
    (0.0, True),
    (complex(1, 2), False),
    ('', True),
    ([], False),
    ({}, False),
    (frozenset(), False),
    (date(2019, 12, 31), False),
    (datetime.now(), False),
])
def test_is_scalar_type(value, expected):
    assert is_scalar(value) == expected
