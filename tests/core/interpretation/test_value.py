from datetime import datetime, timedelta, timezone
from typing import Optional

from pytest import raises

from preacher.core.datetime import StrftimeFormat
from preacher.core.interpretation import (
    Value,
    ValueContext,
    RelativeDatetimeValue,
)

PKG = 'preacher.core.interpretation.value'


def test_incomplete_value():
    class IncompleteValue(Value[object]):
        def resolve(self, context: Optional[ValueContext] = None) -> object:
            return super().resolve(context)

    value = IncompleteValue()
    with raises(NotImplementedError):
        value.resolve(ValueContext())


def test_relative_datetime_value_default(mocker):
    now = datetime(2020, 1, 23, 12, 34, 56, 0, timezone.utc)
    mocker.patch(f'{PKG}.now', return_value=now)

    delta = timedelta(seconds=1)
    value = RelativeDatetimeValue(delta=delta)
    resolved = value.resolve()
    assert resolved.value == now + delta
    assert resolved.formatted == '2020-01-23T12:34:57+00:00'


def test_relative_datetime_value_contextual():
    now = datetime(2020, 12, 31, 1, 23, 45, 123456, timezone.utc)

    delta = timedelta(minutes=-1)
    value = RelativeDatetimeValue(delta, fmt=StrftimeFormat('%H:%M:%S'))
    resolved = value.resolve(ValueContext(origin_datetime=now))
    assert resolved.value == now + delta
    assert resolved.formatted == '01:22:45'
