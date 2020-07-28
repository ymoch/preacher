from unittest.mock import sentinel

from preacher.core.request.request_body import UrlencodedRequestBody

PKG = 'preacher.core.request.request_body'


def test(mocker):
    resolve_params = mocker.patch(f'{PKG}.resolve_url_params')
    resolve_params.return_value = sentinel.resolved_params

    body = UrlencodedRequestBody(sentinel.params)
    assert body.content_type == 'application/x-www-form-urlencoded'

    resolved = body.resolve(sentinel.context)
    assert resolved is sentinel.resolved_params

    resolve_params.assert_called_once_with(sentinel.params, sentinel.context)
