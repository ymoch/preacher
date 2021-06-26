from datetime import datetime, timezone, time, timedelta
from unittest.mock import NonCallableMock, sentinel

from pytest import mark, raises

from preacher.core.datetime import DatetimeWithFormat, ISO8601
from preacher.core.value import ValueContext, Value
from preacher.core.value.impl.datetime import DatetimeValueWithFormat
from preacher.core.value.impl.datetime import OnlyTimeDatetime
from preacher.core.value.impl.datetime import RelativeDatetime
from preacher.core.value.impl.datetime import parse_datetime_value_with_format

PKG = "preacher.core.value.impl.datetime"


def test_only_time_datetime_value_default(mocker):
    now = datetime(2020, 1, 23, 12, 34, 56, 0, tzinfo=timezone.utc)
    mocker.patch(f"{PKG}.now", return_value=now)

    tm = time(1, 23, 45, 678901)
    value = OnlyTimeDatetime(tm)
    assert issubclass(value.type, datetime)

    resolved = value.resolve()
    assert resolved == datetime(2020, 1, 23, 1, 23, 45, 678901)


def test_only_time_datetime_value_contextual():
    now = datetime(2020, 12, 31, 1, 23, 45, 123456, tzinfo=timezone.utc)

    tz = timezone(timedelta(hours=9), "JST")
    tm = time(12, 34, 56, 0, tzinfo=tz)
    value = OnlyTimeDatetime(tm)
    assert issubclass(value.type, datetime)

    resolved = value.resolve(ValueContext(origin_datetime=now))
    assert resolved == datetime(2020, 12, 31, 12, 34, 56, 0, tz)


def test_relative_datetime_value_default(mocker):
    now = datetime(2020, 1, 23, 12, 34, 56, 0, tzinfo=timezone.utc)
    mocker.patch(f"{PKG}.now", return_value=now)

    delta = timedelta(seconds=1)
    value = RelativeDatetime(delta=delta)
    assert issubclass(value.type, datetime)

    resolved = value.resolve()
    assert resolved == now + delta


def test_relative_datetime_value_contextual():
    now = datetime(2020, 12, 31, 1, 23, 45, 123456, tzinfo=timezone.utc)

    delta = timedelta(minutes=-1)
    value = RelativeDatetime(delta)
    assert issubclass(value.type, datetime)

    resolved = value.resolve(ValueContext(origin_datetime=now))
    assert resolved == now + delta


def test_datetime_with_format_default():
    original = NonCallableMock(Value)
    original.resolve.return_value = datetime(2020, 1, 23, 1, 23, 45, 678901)

    value = DatetimeValueWithFormat(original)
    assert value.type == DatetimeWithFormat

    resolved = value.resolve()
    assert resolved.value == datetime(2020, 1, 23, 1, 23, 45, 678901)
    assert resolved.fmt is ISO8601

    original.resolve.assert_called_once_with(None)


def test_datetime_with_format_contextual():
    original = NonCallableMock(Value)
    original.resolve.return_value = datetime(2020, 1, 23, 1, 23, 45, 678901)

    value = DatetimeValueWithFormat(original, sentinel.fmt)
    assert value.type == DatetimeWithFormat

    resolved = value.resolve(sentinel.context)
    assert resolved.value == datetime(2020, 1, 23, 1, 23, 45, 678901)
    assert resolved.fmt is sentinel.fmt

    original.resolve.assert_called_once_with(sentinel.context)


def test_parse_datetime_value_with_format_given_a_naive_datetime(mocker):
    dt_ctor = mocker.patch(f"{PKG}.DatetimeWithFormat", return_value=sentinel.dt)
    value_ctor = mocker.patch(f"{PKG}.StaticValue", return_value=sentinel.value)
    mocker.patch(f"{PKG}.system_timezone", return_value=timezone.utc)

    obj = datetime(2021, 1, 23)
    value = parse_datetime_value_with_format(obj)
    assert value is sentinel.value

    dt_ctor.assert_called_once_with(datetime(2021, 1, 23, tzinfo=timezone.utc), None)
    value_ctor.assert_called_once_with(sentinel.dt)


def test_parse_datetime_value_with_format_given_an_aware_datetime(mocker):
    dt_ctor = mocker.patch(f"{PKG}.DatetimeWithFormat", return_value=sentinel.dt)
    value_ctor = mocker.patch(f"{PKG}.StaticValue", return_value=sentinel.value)

    tz = timezone(timedelta(hours=9))
    obj = datetime(2021, 1, 23, tzinfo=tz)
    value = parse_datetime_value_with_format(obj, sentinel.fmt)
    assert value is sentinel.value

    dt_ctor.assert_called_once_with(datetime(2021, 1, 23, tzinfo=tz), sentinel.fmt)
    value_ctor.assert_called_once_with(sentinel.dt)


def test_parse_datetime_value_with_format_given_time(mocker):
    dt_ctor = mocker.patch(f"{PKG}.OnlyTimeDatetime", return_value=sentinel.dt)
    value_ctor = mocker.patch(f"{PKG}.DatetimeValueWithFormat", return_value=sentinel.value)

    obj = "01:02+09:00"
    value = parse_datetime_value_with_format(obj, sentinel.fmt)
    assert value is sentinel.value

    dt_ctor.assert_called_once_with(time(1, 2, tzinfo=timezone(timedelta(hours=9))))
    value_ctor.assert_called_once_with(sentinel.dt, sentinel.fmt)


def test_parse_datetime_value_with_format_given_timedelta(mocker):
    dt_ctor = mocker.patch(f"{PKG}.RelativeDatetime", return_value=sentinel.dt)
    value_ctor = mocker.patch(f"{PKG}.DatetimeValueWithFormat", return_value=sentinel.value)

    obj = "+1 day"
    value = parse_datetime_value_with_format(obj, sentinel.fmt)
    assert value is sentinel.value

    dt_ctor.assert_called_once_with(timedelta(days=1))
    value_ctor.assert_called_once_with(sentinel.dt, sentinel.fmt)


@mark.parametrize("value", (None, 1, [], "xyz"))
def test_parse_datetime_value_with_format_given_invalid_one(value):
    with raises(ValueError):
        parse_datetime_value_with_format(value)
