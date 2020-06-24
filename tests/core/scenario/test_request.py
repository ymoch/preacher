import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch, sentinel

import requests
from pytest import fixture

from preacher.core.interpretation.value import Value
from preacher.core.scenario.request import Request, ResponseWrapper, Method

PACKAGE = 'preacher.core.scenario.request'


@fixture
def session():
    response = MagicMock(
        spec=requests.Response,
        elapsed=timedelta(seconds=1.23),
        status_code=402,
        headers={'Header-Name': 'Header-Value'},
        text=sentinel.text,
        content=sentinel.content,
    )
    session = MagicMock(requests.Session)
    session.__enter__ = MagicMock(return_value=session)
    session.request = MagicMock(return_value=response)
    return session


@patch('uuid.uuid4', return_value=MagicMock(
    spec=uuid.UUID,
    __str__=MagicMock(return_value='uuid')
))
@patch(f'{PACKAGE}.now', return_value=sentinel.now)
def test_request(now, uuid4, session):
    param_value = MagicMock(Value)
    param_value.apply_context = MagicMock(return_value=sentinel.param_value)

    params = {
        'none': None,
        'false': False,
        'true': True,
        'list': [
            None,
            1,
            1.2,
            'str',
            datetime(2020, 1, 23, 12, 34, 56, tzinfo=timezone.utc),
            param_value,
        ]
    }

    request = Request(
        method=Method.POST,
        path='/path',
        headers={'k1': 'v1'},
        params=params,
    )
    assert request.path == '/path'
    assert request.headers == {'k1': 'v1'}
    assert request.params == params

    with patch('requests.Session', return_value=session):
        response = request('base-url', timeout=5.0)

    assert isinstance(response, ResponseWrapper)
    assert response.id == 'uuid'
    assert response.elapsed == 1.23
    assert response.status_code == 402
    assert response.headers == {'header-name': 'Header-Value'}
    assert response.body.text == sentinel.text
    assert response.body.content == sentinel.content
    assert response.starts == sentinel.now

    uuid4.assert_called()
    now.assert_called()
    param_value.apply_context.assert_called_once_with(
        origin_datetime=sentinel.now,
    )

    args, kwargs = session.request.call_args
    assert args == ('POST', 'base-url/path')
    assert kwargs['headers']['User-Agent'].startswith('Preacher')
    assert kwargs['headers']['k1'].startswith('v1')
    assert kwargs['params']['none'] is None
    assert kwargs['params']['false'] == 'false'
    assert kwargs['params']['true'] == 'true'
    assert kwargs['params']['list'] == [
        None,
        '1',
        '1.2',
        'str',
        '2020-01-23T12:34:56+00:00',
        'sentinel.param_value',
    ]
    assert kwargs['timeout'] == 5.0

    session.__exit__.assert_called()


def test_request_given_string_params(session):
    request = Request(params='foo=bar')
    with patch('requests.Session', return_value=session):
        request('')
    kwargs = session.request.call_args[1]
    assert kwargs['params'] == 'foo=bar'


def test_request_overwrites_default_headers(session):
    request = Request(headers={'User-Agent': 'custom-user-agent'})
    with patch('requests.Session', return_value=session):
        request('base-url')
    kwargs = session.request.call_args[1]
    assert kwargs['headers']['User-Agent'] == 'custom-user-agent'

    # Doesn't change the state.
    request = Request()
    with patch('requests.Session', return_value=session):
        request('base-url')
    kwargs = session.request.call_args[1]
    assert kwargs['headers']['User-Agent'].startswith('Preacher')
    assert kwargs['timeout'] is None
