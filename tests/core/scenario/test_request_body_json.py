from datetime import date, datetime, timezone
from unittest.mock import NonCallableMock, sentinel

from pytest import mark

from preacher.core.interpretation import Value
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
    resolved = body.resolve()
    assert resolved == expected


def test_resolve_given_values():
    value_of_value = NonCallableMock(Value)
    value_of_value.resolve.return_value = date(1234, 1, 2)
    assert isinstance(value_of_value, Value)

    value = NonCallableMock(Value)
    value.resolve.return_value = [value_of_value]
    assert isinstance(value, Value)

    body = JsonRequestBody({'key': value})
    resolved = body.resolve(sentinel.context)
    assert resolved == '{"key":["1234-01-02"]}'

    value.resolve.assert_called_once_with(sentinel.context)
    value_of_value.resolve.assert_called_once_with(sentinel.context)
