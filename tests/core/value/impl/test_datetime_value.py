from datetime import datetime, timezone, time, timedelta
from unittest.mock import NonCallableMock, sentinel

from pytest import mark, raises

from preacher.core.datetime import DatetimeWithFormat, ISO8601
from preacher.core.value import Value
from preacher.core.value.impl.datetime import DatetimeValueWithFormat
from preacher.core.value.impl.datetime import RelativeDatetime
from preacher.core.value.impl.datetime import parse_datetime_value_with_format

PKG = "preacher.core.value.impl.datetime"


def test_only_time_datetime_value_default(mocker):
    now = datetime(2020, 1, 23, 12, 34, 56, 0, tzinfo=timezone.utc)
    mocker.patch(f"{PKG}.now", return_value=now)

    tm = time(1, 23, 45, 678901)
    value = RelativeDatetime(tm=tm)
    assert issubclass(value.type, datetime)

    resolved = value.resolve()
    assert resolved == datetime(2020, 1, 23, 1, 23, 45, 678901)


@mark.parametrize("context", (None, {}))
def test_delta_datetime_value_default(mocker, context):
    now = datetime(2020, 1, 23, 12, 34, 56, 0, tzinfo=timezone.utc)
    mocker.patch(f"{PKG}.now", return_value=now)

    delta = timedelta(seconds=1)
    value = RelativeDatetime(delta=delta)
    assert issubclass(value.type, datetime)

    resolved = value.resolve(context=context)
    assert resolved == now + delta


@mark.parametrize(
    "context",
    (
        {"starts": datetime(2020, 12, 31, 1, 23, 45, 123456, tzinfo=timezone.utc)},
        {"starts": "2020-12-31T01:23:45.123456Z"},
    )
)
def test_combined_relative_datetime_value_contextual(context):
    delta = timedelta(days=-1)
    tz = timezone(timedelta(hours=9), "JST")
    tm = time(12, 34, 56, 12345, tzinfo=tz)
    value = RelativeDatetime(delta=delta, tm=tm)
    assert issubclass(value.type, datetime)

    resolved = value.resolve(context=context)
    assert resolved.year == 2020
    assert resolved.month == 12
    assert resolved.day == 30
    assert resolved.hour == 12
    assert resolved.minute == 34
    assert resolved.second == 56
    assert resolved.microsecond == 12345
    assert resolved.tzinfo is tz


@mark.parametrize("context", ({"starts": 123}, {"starts": "foo"}))
def test_invalid_relative_datetime_value(context):
    value = RelativeDatetime()
    with raises(ValueError):
        value.resolve(context)


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


def test_parse_datetime_value_with_format_empty(mocker):
    dt_ctor = mocker.patch(f"{PKG}.RelativeDatetime", return_value=sentinel.dt)
    value_ctor = mocker.patch(f"{PKG}.DatetimeValueWithFormat", return_value=sentinel.value)

    obj = " 　"  # contains a full-width space character.
    value = parse_datetime_value_with_format(obj, sentinel.fmt)
    assert value is sentinel.value

    dt_ctor.assert_called_once_with(timedelta(), None)
    value_ctor.assert_called_once_with(sentinel.dt, sentinel.fmt)


def test_parse_datetime_value_with_format_combined(mocker):
    dt_ctor = mocker.patch(f"{PKG}.RelativeDatetime", return_value=sentinel.dt)
    value_ctor = mocker.patch(f"{PKG}.DatetimeValueWithFormat", return_value=sentinel.value)

    obj = "+1 hour 12:45-15:00 -1minutes 01:02+09:00"
    value = parse_datetime_value_with_format(obj, sentinel.fmt)
    assert value is sentinel.value

    dt_ctor.assert_called_once_with(
        timedelta(minutes=59),
        time(1, 2, tzinfo=timezone(timedelta(hours=9))),
    )
    value_ctor.assert_called_once_with(sentinel.dt, sentinel.fmt)


@mark.parametrize("value", (None, 1, [], "xyz", "+1", "-1 xyz"))
def test_parse_datetime_value_with_format_given_invalid_one(value):
    with raises(ValueError):
        parse_datetime_value_with_format(value)
