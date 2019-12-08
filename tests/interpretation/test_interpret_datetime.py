from datetime import datetime, timezone, timedelta

from pytest import mark

from preacher.interpretation.datetime import interpret_datetime


UTC = timezone.utc
JST = timezone(timedelta(hours=9))


@mark.parametrize('value, expected', [
    (datetime(2019, 1, 23), datetime(2019, 1, 23, tzinfo=UTC)),
    (datetime(2019, 1, 23, tzinfo=JST), datetime(2019, 1, 23, tzinfo=JST)),
])
def test_interpret_datetime_given_datetime(value, expected):
    assert interpret_datetime(value) == expected
