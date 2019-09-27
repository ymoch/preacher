from unittest.mock import MagicMock

from pytest import fixture, mark

from preacher.core.util import retry_while_false


@fixture
def func():
    return MagicMock(side_effect=[0, 0, 1])


@mark.parametrize('attempts', (
    -1,
    0,
))
@mark.xfail(raises=ValueError)
def test_when_given_invalid_args(func, attempts):
    retry_while_false(func, attempts=attempts)


@mark.parametrize('attempts, expected_result, expected_call_count', (
    (1, 0, 1),
    (2, 0, 2),
    (3, 1, 3),
    (4, 1, 3),
))
def test_retrying(func, attempts, expected_result, expected_call_count):
    actual = retry_while_false(func, attempts=attempts)
    assert actual == expected_result

    assert func.call_count == expected_call_count
