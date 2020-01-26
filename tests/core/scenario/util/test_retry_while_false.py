from unittest.mock import MagicMock, patch, sentinel

from pytest import fixture, mark, raises

from preacher.core.scenario.util.retry import retry_while_false


@fixture
def func():
    return MagicMock(side_effect=[0, 0, 1])


@mark.parametrize('attempts', (-1, 0))
def test_when_given_invalid_args(func, attempts):
    with raises(ValueError):
        retry_while_false(func, attempts=attempts)


@mark.parametrize(
    'attempts, expected_result, expected_call_count, expected_sleep_count',
    (
        (1, 0, 1, 0),
        (2, 0, 2, 1),
        (3, 1, 3, 2),
        (4, 1, 3, 2),
    ),
)
def test_retrying(
    func,
    attempts,
    expected_result,
    expected_call_count,
    expected_sleep_count,
):
    with patch('time.sleep') as sleep:
        actual = retry_while_false(func, attempts=attempts)
    assert actual == expected_result

    assert func.call_count == expected_call_count
    assert sleep.call_count == expected_sleep_count


def test_retrying_with_delay(func):
    with patch('time.sleep') as sleep:
        retry_while_false(func, attempts=2, delay=sentinel.delay)
    sleep.assert_called_once_with(sentinel.delay)
