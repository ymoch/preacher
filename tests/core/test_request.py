from unittest.mock import MagicMock, patch, sentinel

from requests import Response

from preacher.core.request import Request


PACKAGE = 'preacher.core.request'


@patch(f'{PACKAGE}.now', return_value=sentinel.now)
@patch('requests.get')
def test_request(requests_get, now):
    inner_response = MagicMock(
        spec=Response,
        status_code=402,
        headers={'header-key': 'header-value'},
        text='text',
    )
    requests_get.return_value = inner_response

    request = Request(path='/path', params={'key': 'value'})
    assert request.path == '/path'
    assert request.params == {'key': 'value'}

    response = request('base-url')
    assert response.status_code == 402
    assert response.headers == {'header-key': 'header-value'}
    assert response.body == 'text'
    assert response.request_datetime == sentinel.now

    args, kwargs = requests_get.call_args
    assert args == ('base-url/path',)
    assert kwargs['headers']['User-Agent'].startswith('Preacher')
