import uuid
from datetime import timedelta
from unittest.mock import NonCallableMock, Mock, sentinel

import requests
from pytest import fixture

from preacher.core.scenario.request import Request, ResponseWrapper, Method
from preacher.core.scenario.request_body import RequestBody

PACKAGE = 'preacher.core.scenario.request'


@fixture
def session():
    response = NonCallableMock(requests.Response)
    response.elapsed = timedelta(seconds=1.23)
    response.status_code = 402
    response.headers = {'Header-Name': 'Header-Value'}
    response.text = sentinel.text
    response.content = sentinel.content

    session = NonCallableMock(requests.Session)
    session.__enter__ = Mock(return_value=session)
    session.__exit__ = Mock()
    session.request = Mock(return_value=response)
    return session


def test_default_request(mocker, session):
    mocker.patch('requests.Session', return_value=session)

    request = Request()
    assert request.method is Method.GET
    assert request.path == ''
    assert request.headers == {}
    assert request.params == {}
    assert request.body is None

    request('base-url')
    args, kwargs = session.request.call_args
    assert args == ('GET', 'base-url')
    assert kwargs['headers']['User-Agent'].startswith('Preacher')
    assert kwargs['params'] == {}
    assert kwargs['data'] is None
    assert kwargs['timeout'] is None

    session.__enter__.assert_called_once()
    session.__exit__.assert_called_once()


def test_request(mocker, session):
    now = mocker.patch(f'{PACKAGE}.now', return_value=sentinel.now)

    uuid_obj = NonCallableMock(uuid.UUID, __str__=Mock(return_value="id"))
    uuid4 = mocker.patch('uuid.uuid4', return_value=uuid_obj)

    resolve_params = mocker.patch(
        f'{PACKAGE}.resolve_url_params',
        return_value=sentinel.resolved_params,
    )

    body = NonCallableMock(RequestBody)
    body.content_type = sentinel.content_type
    body.resolve = Mock(return_value=sentinel.data)

    request = Request(
        method=Method.POST,
        path='/path',
        headers={'k1': 'v1'},
        params=sentinel.params,
        body=body,
    )
    assert request.method is Method.POST
    assert request.path == '/path'
    assert request.headers == {'k1': 'v1'}
    assert request.params is sentinel.params
    assert request.body is body

    response = request('base-url', timeout=5.0, session=session)
    assert isinstance(response, ResponseWrapper)
    assert response.id == 'id'
    assert response.elapsed == 1.23
    assert response.status_code == 402
    assert response.headers == {'header-name': 'Header-Value'}
    assert response.body.text == sentinel.text
    assert response.body.content == sentinel.content
    assert response.starts == sentinel.now

    uuid4.assert_called()
    now.assert_called()
    resolve_params.assert_called_once_with(
        sentinel.params,
        origin_datetime=sentinel.now,
    )
    body.resolve.assert_called_once_with(origin_datetime=sentinel.now)

    args, kwargs = session.request.call_args
    assert args == ('POST', 'base-url/path')
    assert kwargs['headers']['User-Agent'].startswith('Preacher')
    assert kwargs['headers']['k1'].startswith('v1')
    assert kwargs['headers']['Content-Type'] is sentinel.content_type
    assert kwargs['params'] is sentinel.resolved_params
    assert kwargs['data'] is sentinel.data
    assert kwargs['timeout'] == 5.0


def test_request_overwrites_default_headers(session):
    body = NonCallableMock(RequestBody)
    body.content_type = sentinel.content_type
    body.resolve = Mock(return_value=sentinel.data)

    request = Request(
        headers={
            'User-Agent': sentinel.custom_user_agent,
            'Content-Type': sentinel.custom_content_type,
        },
        body=body,
    )
    request('base-url', session=session)
    kwargs = session.request.call_args[1]
    assert kwargs['headers']['User-Agent'] == sentinel.custom_user_agent
    assert kwargs['headers']['Content-Type'] == sentinel.custom_content_type

    # Doesn't change the state.
    request = Request(body=body)
    request('base-url', session=session)
    kwargs = session.request.call_args[1]
    assert kwargs['headers']['User-Agent'].startswith('Preacher')
    assert kwargs['headers']['Content-Type'] is sentinel.content_type
    assert kwargs['timeout'] is None
