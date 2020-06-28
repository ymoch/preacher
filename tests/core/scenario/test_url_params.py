from datetime import date, datetime, timezone
from unittest.mock import MagicMock, sentinel

from preacher.core.interpretation.value import Value
from preacher.core.scenario.url_param import resolve_url_params


def test_resolve_params_given_a_string():
    resolved = resolve_url_params('foo=bar')
    assert resolved == 'foo=bar'


def test_resolve_params_given_a_mapping():
    value = MagicMock(Value)
    value.apply_context.return_value = sentinel.resolved_value

    params = {
        'none': None,
        'false': False,
        'true': True,
        'list': [
            None,
            1,
            1.2,
            'str',
            date(2020, 12, 31),
            datetime(2020, 1, 23, 12, 34, 56, tzinfo=timezone.utc),
            value,
        ]
    }
    resolved = resolve_url_params(params, foo=sentinel.foo)

    assert resolved['none'] is None
    assert resolved['false'] == 'false'
    assert resolved['true'] == 'true'
    assert resolved['list'] == [
        None,
        '1',
        '1.2',
        'str',
        '2020-12-31',
        '2020-01-23T12:34:56+00:00',
        'sentinel.resolved_value',
    ]

    value.apply_context.assert_called_once_with(foo=sentinel.foo)
