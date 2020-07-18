from unittest.mock import patch, sentinel

from preacher.compilation.verification.response_body import (
    ResponseBodyDescriptionCompiled,
)
from preacher.core.verification import analyze_json_str

PKG = 'preacher.compilation.verification.response_body'


ctor_patch = patch(
    target=f'{PKG}.ResponseBodyDescription',
    return_value=sentinel.fixed,
)


def test_replace():
    initial = ResponseBodyDescriptionCompiled(
        analyze=sentinel.initial_analyze,
        descriptions=sentinel.initial_descriptions,
    )

    other = ResponseBodyDescriptionCompiled()
    replaced = initial.replace(other)
    assert replaced.analyze is sentinel.initial_analyze
    assert replaced.descriptions is sentinel.initial_descriptions

    other = ResponseBodyDescriptionCompiled(
        analyze=sentinel.analyze,
        descriptions=sentinel.descriptions,
    )
    replaced = initial.replace(other)
    assert replaced.analyze is sentinel.analyze
    assert replaced.descriptions is sentinel.descriptions


@ctor_patch
def test_fix_hollow(ctor):
    compiled = ResponseBodyDescriptionCompiled()
    fixed = compiled.fix()
    assert fixed is sentinel.fixed

    ctor.assert_called_once_with(
        analyze=analyze_json_str,
        descriptions=None,
    )


@ctor_patch
def test_fix_filled(ctor):
    compiled = ResponseBodyDescriptionCompiled(
        analyze=sentinel.analyze,
        descriptions=sentinel.descriptions,
    )
    fixed = compiled.fix()
    assert fixed is sentinel.fixed

    ctor.assert_called_once_with(
        analyze=sentinel.analyze,
        descriptions=sentinel.descriptions,
    )
