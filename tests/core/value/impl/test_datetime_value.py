from datetime import datetime, timezone, time, timedelta
from unittest.mock import NonCallableMock, sentinel

from preacher.core.datetime import DatetimeWithFormat, ISO8601
from preacher.core.value import ValueContext, Value
from preacher.core.value.impl.datetime import DatetimeValueWithFormat
from preacher.core.value.impl.datetime import OnlyTimeDatetime
from preacher.core.value.impl.datetime import RelativeDatetime

PKG = 'preacher.core.value.impl.datetime'


def test_only_time_datetime_value_default(mocker):
    now = datetime(2020, 1, 23, 12, 34, 56, 0, tzinfo=timezone.utc)
    mocker.patch(f'{PKG}.now', return_value=now)

    tm = time(1, 23, 45, 678901)
    value = OnlyTimeDatetime(tm)
    assert issubclass(value.type, datetime)

    resolved = value.resolve()
    assert resolved == datetime(2020, 1, 23, 1, 23, 45, 678901)


def test_only_time_datetime_value_contextual():
    now = datetime(2020, 12, 31, 1, 23, 45, 123456, tzinfo=timezone.utc)

    tz = timezone(timedelta(hours=9), 'JST')
    tm = time(12, 34, 56, 0, tzinfo=tz)
    value = OnlyTimeDatetime(tm)
    assert issubclass(value.type, datetime)

    resolved = value.resolve(ValueContext(origin_datetime=now))
    assert resolved == datetime(2020, 12, 31, 12, 34, 56, 0, tz)


def test_relative_datetime_value_default(mocker):
    now = datetime(2020, 1, 23, 12, 34, 56, 0, tzinfo=timezone.utc)
    mocker.patch(f'{PKG}.now', return_value=now)

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
