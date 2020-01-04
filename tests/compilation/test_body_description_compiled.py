from unittest.mock import patch, sentinel

from preacher.compilation.body import BodyDescriptionCompiled
from preacher.core.analysis import analyze_json_str

ctor_patch = patch(
    target='preacher.compilation.body.BodyDescription',
    return_value=sentinel.fixed,
)


def test_replace():
    initial = BodyDescriptionCompiled(
        analyze=sentinel.initial_analyze,
        descriptions=sentinel.initial_descriptions,
    )

    other = BodyDescriptionCompiled()
    replaced = initial.replace(other)
    assert replaced.analyze is sentinel.initial_analyze
    assert replaced.descriptions is sentinel.initial_descriptions

    other = BodyDescriptionCompiled(
        analyze=sentinel.analyze,
        descriptions=sentinel.descriptions,
    )
    replaced = initial.replace(other)
    assert replaced.analyze is sentinel.analyze
    assert replaced.descriptions is sentinel.descriptions


@ctor_patch
def test_fix_hollow(ctor):
    compiled = BodyDescriptionCompiled()
    fixed = compiled.fix()
    assert fixed is sentinel.fixed

    ctor.assert_called_once_with(
        analyze=analyze_json_str,
        descriptions=None,
    )


@ctor_patch
def test_fix_filled(ctor):
    compiled = BodyDescriptionCompiled(
        analyze=sentinel.analyze,
        descriptions=sentinel.descriptions,
    )
    fixed = compiled.fix()
    assert fixed is sentinel.fixed

    ctor.assert_called_once_with(
        analyze=sentinel.analyze,
        descriptions=sentinel.descriptions,
    )
