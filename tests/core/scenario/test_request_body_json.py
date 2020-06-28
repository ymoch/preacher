from datetime import date, datetime, timezone
from unittest.mock import NonCallableMock, Mock

from pytest import mark

from preacher.core.interpretation.value import Value
from preacher.core.scenario.request_body import JsonRequestBody


def test_content_type():
    body = JsonRequestBody(1)
    assert body.content_type == 'application/json'


@mark.parametrize(('data', 'expected'), [
    (None, 'null'),
    ([1, 1.2], '[1,1.2]'),
    ({'date': date(2020, 1, 23)}, '{"date":"2020-01-23"}'),
    (
        datetime(2020, 1, 23, 12, 34, 56, 0, tzinfo=timezone.utc),
        '"2020-01-23T12:34:56+00:00"',
    )
])
def test_resolve_simple(data, expected):
    body = JsonRequestBody(data)
    resolved = body.resolve(foo='bar')
    assert resolved == expected


def test_resolve_given_values():
    value_of_value = NonCallableMock(Value)
    value_of_value.apply_context = Mock(return_value=date(1234, 1, 2))
    assert isinstance(value_of_value, Value)
    value = NonCallableMock(Value)
    value.apply_context = Mock(return_value=[value_of_value])
    assert isinstance(value, Value)

    body = JsonRequestBody({'key': value})
    resolved = body.resolve(foo='bar')
    assert resolved == '{"key":["1234-01-02"]}'
