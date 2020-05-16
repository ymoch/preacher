from datetime import date, datetime

from pytest import mark, raises

from preacher.compilation.error import CompilationError
from preacher.compilation.type import ensure_scalar


@mark.parametrize('value', [
    None,
    complex(1, 2),
    [],
    {},
    frozenset(),
    (date(2019, 12, 31), False),
])
def test_ensure_scalar_raises_compilation_error(value):
    with raises(CompilationError):
        ensure_scalar(value)


@mark.parametrize('value, expected', [
    (False, False),
    (0, 0),
    (0.0, 0.0),
    ('', ''),
    (
        datetime.fromisoformat('2020-04-01T01:23:45+09:00'),
        '2020-04-01T01:23:45+09:00',
    )
])
def test_ensure_scalar_returns_value(value, expected):
    assert ensure_scalar(value) == expected
