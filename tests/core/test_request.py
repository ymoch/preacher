import uuid
from unittest.mock import MagicMock, patch, sentinel

from requests import Response

from preacher.core.request import Request


PACKAGE = 'preacher.core.request'


@patch('uuid.uuid4', return_value=MagicMock(
    spec=uuid.UUID,
    __str__=MagicMock(return_value='uuid')
))
@patch(f'{PACKAGE}.now', return_value=sentinel.now)
@patch('requests.get', return_value=MagicMock(
    spec=Response,
    status_code=402,
    headers={'Header-Name': 'Header-Value'},
    text='text',
))
def test_request(requests_get, now, uuid4):
    request = Request(path='/path', headers={'k1': 'v1'}, params={'k2': 'v2'})
    assert request.path == '/path'
    assert request.headers == {'k1': 'v1'}
    assert request.params == {'k2': 'v2'}

    response = request('base-url', timeout=5.0)
    assert response.id == 'uuid'
    assert response.status_code == 402
    assert response.headers == {'header-name': 'Header-Value'}
    assert response.body == 'text'
    assert response.request_datetime == sentinel.now

    uuid4.assert_called()
    now.assert_called()

    args, kwargs = requests_get.call_args
    assert args == ('base-url/path',)
    assert kwargs['headers']['User-Agent'].startswith('Preacher')
    assert kwargs['headers']['k1'].startswith('v1')
    assert kwargs['params']['k2'].startswith('v2')
    assert kwargs['timeout'] == 5.0


@patch('requests.get', return_value=MagicMock(
    spec=Response,
    status_code=402,
    headers={'header-key': 'header-value'},
    text='text',
))
def test_request_overwrites_default_headers(requests_get):
    Request(headers={'User-Agent': 'custom-user-agent'})('base-url')
    kwargs = requests_get.call_args[1]
    assert kwargs['headers']['User-Agent'] == 'custom-user-agent'

    # Doesn't change the state.
    Request()('base-url')
    kwargs = requests_get.call_args[1]
    assert kwargs['headers']['User-Agent'].startswith('Preacher')
    assert kwargs['timeout'] is None
