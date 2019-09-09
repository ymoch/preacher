from unittest.mock import MagicMock, patch, sentinel

from requests import Response

from preacher.core.request import Request


PACKAGE = 'preacher.core.request'


@patch(f'{PACKAGE}.now', return_value=sentinel.now)
@patch('requests.get', return_value=MagicMock(
    spec=Response,
    status_code=402,
    headers={'header-key': 'header-value'},
    text='text',
))
def test_request(requests_get, now):
    request = Request(path='/path', headers={'k1': 'v1'}, params={'k2': 'v2'})
    assert request.path == '/path'
    assert request.headers == {'k1': 'v1'}
    assert request.params == {'k2': 'v2'}

    response = request('base-url')
    assert response.status_code == 402
    assert response.headers == {'header-key': 'header-value'}
    assert response.body == 'text'
    assert response.request_datetime == sentinel.now

    args, kwargs = requests_get.call_args
    assert args == ('base-url/path',)
    assert kwargs['headers']['User-Agent'].startswith('Preacher')
    assert kwargs['headers']['k1'].startswith('v1')
    assert kwargs['params']['k2'].startswith('v2')


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
