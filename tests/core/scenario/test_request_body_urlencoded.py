from unittest.mock import sentinel

from preacher.core.scenario.request_body import UrlencodedRequestBody

PACKAGE = 'preacher.core.scenario.request_body'


def test(mocker):
    resolve_params = mocker.patch(
        f'{PACKAGE}.resolve_url_params',
        return_value=sentinel.resolved_params,
    )

    body = UrlencodedRequestBody(sentinel.params)
    assert body.content_type == 'application/x-www-form-urlencoded'

    resolved = body.resolve(foo='bar')
    assert resolved is sentinel.resolved_params

    resolve_params.assert_called_once_with(sentinel.params, foo='bar')
