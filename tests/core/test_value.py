from datetime import datetime, time, timedelta, timezone
from typing import Optional, Type

from pytest import raises

from preacher.core.datetime import StrftimeFormat, DatetimeWithFormat
from preacher.core.value import (
    Value,
    ValueContext,
    OnlyTimeDatetime,
    RelativeDatetime,
    StaticValue,
)

PKG = 'preacher.core.value'


def test_incomplete_value():
    class IncompleteValue(Value[object]):
        @property
        def type(self) -> Type[object]:
            return super().type

        def resolve(self, context: Optional[ValueContext] = None) -> object:
            return super().resolve(context)

    value = IncompleteValue()
    with raises(NotImplementedError):
        assert value.type == object
    with raises(NotImplementedError):
        value.resolve(ValueContext())


def test_static_value():
    value = StaticValue(1)
    assert issubclass(value.type, int)
    assert value.resolve() == 1


def test_only_time_datetime_value_default(mocker):
    now = datetime(2020, 1, 23, 12, 34, 56, 0, tzinfo=timezone.utc)
    mocker.patch(f'{PKG}.now', return_value=now)

    tm = time(1, 23, 45, 678901)
    value = OnlyTimeDatetime(tm)
    assert issubclass(value.type, DatetimeWithFormat)

    resolved = value.resolve()
    assert resolved.value == datetime(2020, 1, 23, 1, 23, 45, 678901)
    assert resolved.formatted == '2020-01-23T01:23:45.678901'


def test_only_time_datetime_value_contextual():
    now = datetime(2020, 12, 31, 1, 23, 45, 123456, tzinfo=timezone.utc)

    tz = timezone(timedelta(hours=9), 'JST')
    tm = time(12, 34, 56, 0, tzinfo=tz)
    value = OnlyTimeDatetime(tm, fmt=StrftimeFormat('%H:%M:%S%z'))
    assert issubclass(value.type, DatetimeWithFormat)

    resolved = value.resolve(ValueContext(origin_datetime=now))
    assert resolved.value == datetime(2020, 12, 31, 12, 34, 56, 0, tz)
    assert resolved.formatted == '12:34:56+0900'


def test_relative_datetime_value_default(mocker):
    now = datetime(2020, 1, 23, 12, 34, 56, 0, tzinfo=timezone.utc)
    mocker.patch(f'{PKG}.now', return_value=now)

    delta = timedelta(seconds=1)
    value = RelativeDatetime(delta=delta)
    assert issubclass(value.type, DatetimeWithFormat)

    resolved = value.resolve()
    assert resolved.value == now + delta
    assert resolved.formatted == '2020-01-23T12:34:57+00:00'


def test_relative_datetime_value_contextual():
    now = datetime(2020, 12, 31, 1, 23, 45, 123456, tzinfo=timezone.utc)

    delta = timedelta(minutes=-1)
    value = RelativeDatetime(delta, fmt=StrftimeFormat('%H:%M:%S'))
    assert issubclass(value.type, DatetimeWithFormat)

    resolved = value.resolve(ValueContext(origin_datetime=now))
    assert resolved.value == now + delta
    assert resolved.formatted == '01:22:45'
