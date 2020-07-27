from unittest.mock import patch, sentinel

from preacher.compilation.verification.response_body import ResponseBodyDescriptionCompiled

PKG = 'preacher.compilation.verification.response_body'


ctor_patch = patch(f'{PKG}.ResponseBodyDescription', return_value=sentinel.fixed)


def test_replace():
    initial = ResponseBodyDescriptionCompiled(sentinel.initial_descriptions)

    other = ResponseBodyDescriptionCompiled()
    replaced = initial.replace(other)
    assert replaced.descriptions is sentinel.initial_descriptions

    other = ResponseBodyDescriptionCompiled(sentinel.descriptions)
    replaced = initial.replace(other)
    assert replaced.descriptions is sentinel.descriptions


@ctor_patch
def test_fix_hollow(ctor):
    compiled = ResponseBodyDescriptionCompiled()
    fixed = compiled.fix()
    assert fixed is sentinel.fixed

    ctor.assert_called_once_with(None)


@ctor_patch
def test_fix_filled(ctor):
    compiled = ResponseBodyDescriptionCompiled(sentinel.descriptions)
    fixed = compiled.fix()
    assert fixed is sentinel.fixed

    ctor.assert_called_once_with(sentinel.descriptions)
