from unittest.mock import patch, sentinel

from preacher.compilation.request import RequestCompiled
from preacher.core.scenario import Method

ctor_patch = patch(
    target='preacher.compilation.request.Request',
    return_value=sentinel.fixed,
)


def test_replace():
    initial = RequestCompiled(
        method=sentinel.initial_method,
        path=sentinel.initial_path,
        headers=sentinel.initial_headers,
        params=sentinel.initial_params,
    )

    other = RequestCompiled()
    replaced = initial.replace(other)
    assert replaced.method is sentinel.initial_method
    assert replaced.path is sentinel.initial_path
    assert replaced.headers is sentinel.initial_headers
    assert replaced.params is sentinel.initial_params

    other = RequestCompiled(
        method=sentinel.method,
        path=sentinel.path,
        headers=sentinel.headers,
        params=sentinel.params,
    )
    replaced = initial.replace(other)
    assert replaced.method is sentinel.method
    assert replaced.path is sentinel.path
    assert replaced.headers is sentinel.headers
    assert replaced.params is sentinel.params


@ctor_patch
def test_fix_hollow(ctor):
    compiled = RequestCompiled()
    fixed = compiled.fix()
    assert fixed is sentinel.fixed

    ctor.assert_called_once_with(
        method=Method.GET,
        path='',
        headers=None,
        params=None,
    )


@ctor_patch
def test_fix_filled(ctor):
    compiled = RequestCompiled(
        method=sentinel.method,
        path=sentinel.path,
        headers=sentinel.headers,
        params=sentinel.params,
    )
    fixed = compiled.fix()
    assert fixed is sentinel.fixed

    ctor.assert_called_once_with(
        method=sentinel.method,
        path=sentinel.path,
        headers=sentinel.headers,
        params=sentinel.params,
    )
