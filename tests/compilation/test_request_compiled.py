from unittest.mock import Mock, NonCallableMock, sentinel

from preacher.compilation.request import RequestCompiled
from preacher.compilation.request_body import RequestBodyCompiled
from preacher.core.scenario import Method

PACKAGE = 'preacher.compilation.request'


def test_replace():
    initial = RequestCompiled(
        method=sentinel.initial_method,
        path=sentinel.initial_path,
        headers=sentinel.initial_headers,
        params=sentinel.initial_params,
        body=sentinel.initial_body,
    )

    other = RequestCompiled()
    replaced = initial.replace(other)
    assert replaced.method is sentinel.initial_method
    assert replaced.path is sentinel.initial_path
    assert replaced.headers is sentinel.initial_headers
    assert replaced.params is sentinel.initial_params
    assert replaced.body is sentinel.initial_body

    other = RequestCompiled(
        method=sentinel.method,
        path=sentinel.path,
        headers=sentinel.headers,
        params=sentinel.params,
        body=sentinel.body,
    )
    replaced = initial.replace(other)
    assert replaced.method is sentinel.method
    assert replaced.path is sentinel.path
    assert replaced.headers is sentinel.headers
    assert replaced.params is sentinel.params
    assert replaced.body is sentinel.body


def test_fix_hollow(mocker):
    ctor = mocker.patch(f'{PACKAGE}.Request', return_value=sentinel.fixed)

    compiled = RequestCompiled()
    fixed = compiled.fix()
    assert fixed is sentinel.fixed

    ctor.assert_called_once_with(
        method=Method.GET,
        path='',
        headers=None,
        params=None,
        body=None,
    )


def test_fix_filled(mocker):
    ctor = mocker.patch(f'{PACKAGE}.Request', return_value=sentinel.fixed)

    body = NonCallableMock(RequestBodyCompiled)
    body.fix = Mock(return_value=sentinel.body)
    compiled = RequestCompiled(
        method=sentinel.method,
        path=sentinel.path,
        headers=sentinel.headers,
        params=sentinel.params,
        body=body,
    )
    fixed = compiled.fix()
    assert fixed is sentinel.fixed

    ctor.assert_called_once_with(
        method=sentinel.method,
        path=sentinel.path,
        headers=sentinel.headers,
        params=sentinel.params,
        body=sentinel.body,
    )
    body.fix.assert_called_once_with()
