from datetime import datetime, timezone, timedelta
from unittest.mock import patch

from pytest import mark

from preacher.interpretation.datetime import interpret_datetime

PACKAGE = 'preacher.interpretation.datetime'
UTC = timezone.utc
JST = timezone(timedelta(hours=9))


@mark.parametrize('value, expected', [
    (datetime(2019, 1, 23), datetime(2019, 1, 23, tzinfo=UTC)),
    (datetime(2019, 1, 23, tzinfo=JST), datetime(2019, 1, 23, tzinfo=JST)),
])
def test_interpret_datetime_given_datetime(value, expected):
    assert interpret_datetime(value) == expected


@patch(f'{PACKAGE}.interpret_timedelta', return_value=timedelta(days=1))
@patch(f'{PACKAGE}.now', return_value=datetime(2019, 1, 2, tzinfo=UTC))
def test_interpret_datetime_given_timedelta_and_no_kwargs(
    now,
    interpret_timedelta,
):
    assert interpret_datetime('now') == datetime(2019, 1, 3, tzinfo=UTC)
    interpret_timedelta.assert_called_once_with('now')
    now.assert_called_once_with()


@patch(f'{PACKAGE}.interpret_timedelta', return_value=timedelta(days=2))
@patch(f'{PACKAGE}.now')
def test_interpret_datetime_given_timedelta_and_request_datetime(
    now,
    interpret_timedelta,
):
    actual = interpret_datetime(
        '+1 day',
        request_datetime=datetime(2019, 2, 3, tzinfo=JST),
    )
    assert actual == datetime(2019, 2, 5, tzinfo=JST)
    interpret_timedelta.assert_called_once_with('+1 day')
    now.assert_not_called()
