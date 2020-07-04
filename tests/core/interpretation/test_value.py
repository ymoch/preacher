from datetime import timedelta, datetime
from unittest.mock import patch

from pytest import raises

from preacher.core.interpretation.value import Value, RelativeDatetimeValue

PACKAGE = 'preacher.core.interpretation.value'
NOW = datetime.now()


def test_incomplete_value():
    class IncompleteValue(Value[object]):
        def resolve(self, **context) -> object:
            return super().resolve(**context)

    value = IncompleteValue()
    with raises(NotImplementedError):
        value.resolve(key='value')


def test_relative_datetime_value_default():
    delta = timedelta(seconds=1)
    value = RelativeDatetimeValue(delta=delta)
    with patch(f'{PACKAGE}.now', return_value=NOW):
        value_in_context = value.resolve()
    assert value_in_context == NOW + delta


def test_relative_datetime_value_contextual():
    delta = timedelta(minutes=-1)
    value = RelativeDatetimeValue(delta)
    value_in_context = value.resolve(origin_datetime=NOW)
    assert value_in_context == NOW + delta
