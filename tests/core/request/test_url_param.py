from datetime import date, datetime, timezone
from unittest.mock import NonCallableMock, sentinel

from preacher.core.datetime import DatetimeWithFormat
from preacher.core.request.url_param import resolve_url_params
from preacher.core.value import Value


def test_resolve_params_given_a_string():
    resolved = resolve_url_params("foo=bar")
    assert resolved == "foo=bar"


def test_resolve_params_given_a_mapping():
    value = NonCallableMock(Value)
    value.resolve.return_value = "resolved"
    values = NonCallableMock(Value)
    values.resolve.return_value = ["foo", value]

    params = {
        "none": None,
        "false": False,
        "true": True,
        "value": value,
        "values": values,
        "list": [
            None,
            1,
            1.2,
            "str",
            date(2020, 12, 31),
            datetime(2020, 1, 23, 12, 34, 56, tzinfo=timezone.utc),
            NonCallableMock(DatetimeWithFormat, formatted="formatted"),
            value,
        ],
    }
    resolved = resolve_url_params(params, sentinel.context)

    assert resolved["none"] is None
    assert resolved["false"] == "false"
    assert resolved["true"] == "true"
    assert resolved["value"] == "resolved"
    assert resolved["values"] == ["foo", "resolved"]
    assert resolved["list"] == [
        None,
        "1",
        "1.2",
        "str",
        "2020-12-31",
        "2020-01-23T12:34:56+00:00",
        "formatted",
        "resolved",
    ]

    assert value.resolve.call_count == 3
    value.resolve.assert_called_with(sentinel.context)
