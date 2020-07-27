from unittest.mock import patch, sentinel

from preacher.compilation.verification.response import ResponseDescriptionCompiled

PKG = 'preacher.compilation.verification.response'

ctor_patch = patch(f'{PKG}.ResponseDescription', return_value=sentinel.fixed)


def test_replace():
    initial = ResponseDescriptionCompiled(
        status_code=sentinel.initial_status_code,
        headers=sentinel.initial_headers,
        body=sentinel.initial_body,
    )

    other = ResponseDescriptionCompiled()
    replaced = initial.replace(other)
    assert replaced.status_code is sentinel.initial_status_code
    assert replaced.headers is sentinel.initial_headers
    assert replaced.body is sentinel.initial_body

    other = ResponseDescriptionCompiled(
        status_code=sentinel.status_code,
        headers=sentinel.headers,
        body=sentinel.body,
    )
    replaced = initial.replace(other)
    assert replaced.status_code is sentinel.status_code
    assert replaced.headers is sentinel.headers
    assert replaced.body is sentinel.body


@ctor_patch
def test_fix_hollow(ctor):
    compiled = ResponseDescriptionCompiled()
    fixed = compiled.fix()
    assert fixed is sentinel.fixed

    ctor.assert_called_once_with(status_code=None, headers=None, body=None)


@ctor_patch
def test_fix_filled(ctor):
    compiled = ResponseDescriptionCompiled(
        status_code=sentinel.status_code,
        headers=sentinel.headers,
        body=sentinel.body,
    )
    fixed = compiled.fix()
    assert fixed is sentinel.fixed

    ctor.assert_called_once_with(
        status_code=sentinel.status_code,
        headers=sentinel.headers,
        body=sentinel.body,
    )
