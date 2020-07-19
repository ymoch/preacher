import uuid
from datetime import timedelta
from unittest.mock import NonCallableMock, NonCallableMagicMock, sentinel

import requests
from pytest import fixture

from preacher.core.request.request import Request, ResponseWrapper, Method
from preacher.core.request.request_body import RequestBody
from preacher.core.value import ValueContext

PKG = 'preacher.core.request.request'


@fixture
def session():
    response = NonCallableMock(requests.Response)
    response.elapsed = timedelta(seconds=1.23)
    response.status_code = 402
    response.headers = {'Header-Name': 'Header-Value'}
    response.text = sentinel.text
    response.content = sentinel.content

    session = NonCallableMagicMock(requests.Session)
    session.__enter__.return_value = session
    session.send.return_value = response
    return session


@fixture
def body():
    mock = NonCallableMock(RequestBody)
    mock.content_type = 'application/x-www-form-urlencoded'
    mock.resolve.return_value = {'x': 'y', 'name': ['東京', '京都']}
    return mock


def test_default_request(mocker, session):
    mocker.patch('requests.Session', return_value=session)

    request = Request()
    assert request.method is Method.GET
    assert request.path == ''
    assert request.headers == {}
    assert request.params == {}
    assert request.body is None

    request.execute('http://base-url.org')

    args, kwargs = session.send.call_args
    req: requests.PreparedRequest = args[0]
    assert req.method == 'GET'
    assert req.url == 'http://base-url.org/'
    assert req.headers['User-Agent'].startswith('Preacher')
    assert req.body is None
    assert kwargs['timeout'] is None

    session.__enter__.assert_called_once()
    session.__exit__.assert_called_once()


def test_request(mocker, session, body):
    now = mocker.patch(f'{PKG}.now', return_value=sentinel.now)

    uuid_obj = NonCallableMagicMock(uuid.UUID)
    uuid_obj.__str__.return_value = "id"
    uuid4 = mocker.patch('uuid.uuid4', return_value=uuid_obj)

    resolve_params = mocker.patch(f'{PKG}.resolve_url_params')
    resolve_params.return_value = {'name': '東京', 'a': ['b', 'c']}

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

    response = request.execute('https://a.com', timeout=5.0, session=session)
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

    expected_context = ValueContext(origin_datetime=sentinel.now)
    resolve_params.assert_called_once_with(sentinel.params, expected_context)
    body.resolve.assert_called_once_with(expected_context)

    args, kwargs = session.send.call_args
    req: requests.PreparedRequest = args[0]
    assert req.method == 'POST'
    assert req.url == 'https://a.com/path?name=%E6%9D%B1%E4%BA%AC&a=b&a=c'
    assert req.headers['Content-Type'] == 'application/x-www-form-urlencoded'
    assert req.headers['User-Agent'].startswith('Preacher')
    assert req.headers['k1'] == 'v1'
    assert req.body == 'x=y&name=%E6%9D%B1%E4%BA%AC&name=%E4%BA%AC%E9%83%BD'
    assert kwargs['timeout'] == 5.0


def test_request_overwrites_default_headers(session, body):
    request = Request(
        headers={
            'User-Agent': 'custom-user-agent',
            'Content-Type': 'custom-content-type',
        },
        body=body,
    )
    request.execute('https://base-url.net', session=session)
    req: requests.PreparedRequest = session.send.call_args[0][0]
    assert req.headers['User-Agent'] == 'custom-user-agent'
    assert req.headers['Content-Type'] == 'custom-content-type'

    # Doesn't change the state.
    request = Request(body=body)
    request.execute('https://base-url.net', session=session)
    req: requests.PreparedRequest = session.send.call_args[0][0]
    assert req.headers['User-Agent'].startswith('Preacher')
    assert req.headers['Content-Type'] == 'application/x-www-form-urlencoded'
