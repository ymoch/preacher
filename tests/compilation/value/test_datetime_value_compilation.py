from datetime import datetime, time, timedelta, timezone
from unittest.mock import sentinel

from pytest import mark, raises

from preacher.compilation.error import CompilationError
from preacher.compilation.value.datetime import compile_datetime_value_with_format

PKG = 'preacher.compilation.value.datetime'


def test_datetime_value_with_format_given_a_naive_datetime(mocker):
    dt_ctor = mocker.patch(f'{PKG}.DatetimeWithFormat', return_value=sentinel.dt)
    value_ctor = mocker.patch(f'{PKG}.StaticValue', return_value=sentinel.value)
    mocker.patch(f'{PKG}.system_timezone', return_value=timezone.utc)

    obj = datetime(2021, 1, 23)
    value = compile_datetime_value_with_format(obj)
    assert value is sentinel.value

    dt_ctor.assert_called_once_with(datetime(2021, 1, 23, tzinfo=timezone.utc), None)
    value_ctor.assert_called_once_with(sentinel.dt)


def test_datetime_value_with_format_given_an_aware_datetime(mocker):
    dt_ctor = mocker.patch(f'{PKG}.DatetimeWithFormat', return_value=sentinel.dt)
    value_ctor = mocker.patch(f'{PKG}.StaticValue', return_value=sentinel.value)

    tz = timezone(timedelta(hours=9))
    obj = datetime(2021, 1, 23, tzinfo=tz)
    value = compile_datetime_value_with_format(obj, sentinel.fmt)
    assert value is sentinel.value

    dt_ctor.assert_called_once_with(datetime(2021, 1, 23, tzinfo=tz), sentinel.fmt)
    value_ctor.assert_called_once_with(sentinel.dt)


def test_datetime_value_with_format_given_time(mocker):
    dt_ctor = mocker.patch(f'{PKG}.OnlyTimeDatetime', return_value=sentinel.dt)
    value_ctor = mocker.patch(f'{PKG}.DatetimeValueWithFormat', return_value=sentinel.value)

    obj = '01:02+09:00'
    value = compile_datetime_value_with_format(obj, sentinel.fmt)
    assert value is sentinel.value

    dt_ctor.assert_called_once_with(time(1, 2, tzinfo=timezone(timedelta(hours=9))))
    value_ctor.assert_called_once_with(sentinel.dt, sentinel.fmt)


def test_datetime_value_with_format_given_timedelta(mocker):
    dt_ctor = mocker.patch(f'{PKG}.RelativeDatetime', return_value=sentinel.dt)
    value_ctor = mocker.patch(f'{PKG}.DatetimeValueWithFormat', return_value=sentinel.value)

    obj = '+1 day'
    value = compile_datetime_value_with_format(obj, sentinel.fmt)
    assert value is sentinel.value

    dt_ctor.assert_called_once_with(timedelta(days=1))
    value_ctor.assert_called_once_with(sentinel.dt, sentinel.fmt)


@mark.parametrize('value', (None, 1, [], 'xyz'))
def test_datetime_value_with_format_given_invalid_one(value):
    with raises(CompilationError):
        compile_datetime_value_with_format(value)
