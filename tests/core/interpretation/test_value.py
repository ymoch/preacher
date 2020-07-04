from datetime import timedelta, datetime
from typing import Optional

from pytest import raises

from preacher.core.interpretation.value import (
    Value,
    RelativeDatetimeValue,
    ValueContext,
)

PKG = 'preacher.core.interpretation.value'
NOW = datetime.now()


def test_incomplete_value():
    class IncompleteValue(Value[object]):
        def resolve(self, context: Optional[ValueContext] = None) -> object:
            return super().resolve(context)

    value = IncompleteValue()
    with raises(NotImplementedError):
        value.resolve(ValueContext())


def test_relative_datetime_value_default(mocker):
    mocker.patch(f'{PKG}.now', return_value=NOW)

    delta = timedelta(seconds=1)
    value = RelativeDatetimeValue(delta=delta)
    resolved = value.resolve()
    assert resolved == NOW + delta


def test_relative_datetime_value_contextual():
    delta = timedelta(minutes=-1)
    value = RelativeDatetimeValue(delta)
    resolved = value.resolve(ValueContext(origin_datetime=NOW))
    assert resolved == NOW + delta
