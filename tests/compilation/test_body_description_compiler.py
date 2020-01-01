from unittest.mock import MagicMock, call, sentinel, patch

from pytest import fixture, mark, raises

from preacher.compilation.analysis import AnalysisCompiler
from preacher.compilation.body import BodyDescriptionCompiler
from preacher.compilation.description import DescriptionCompiler
from preacher.compilation.error import CompilationError
from preacher.core.analysis import analyze_json_str
from preacher.core.body import BodyDescription

ctor_patch = patch(
    'preacher.compilation.body.BodyDescription',
    return_value=sentinel.body,
)


@fixture
def compiler(analysis, description) -> BodyDescriptionCompiler:
    return BodyDescriptionCompiler(analysis, description)


@fixture
def analysis():
    return MagicMock(
        spec=AnalysisCompiler,
        compile=MagicMock(return_value=sentinel.analyze),
    )


@fixture
def description():
    return MagicMock(
        spec=DescriptionCompiler,
        compile=MagicMock(return_value=sentinel.desc),
    )


@mark.parametrize('value', (None, 0, ''))
def test_given_invalid_values(compiler, value):
    with raises(CompilationError):
        compiler.compile(value)


@mark.parametrize('value', ([], {}))
@ctor_patch
def test_given_empty_values(ctor, value, compiler, analysis, description):
    desc = compiler.compile(value)
    assert desc is sentinel.body

    ctor.assert_called_once_with(analyze=analyze_json_str, descriptions=[])
    analysis.compile.assert_not_called()
    description.compile.assert_not_called()


@ctor_patch
def test_given_a_list(ctor, compiler, analysis, description):
    desc = compiler.compile(['d1', 'd2'])
    assert desc is sentinel.body

    ctor.assert_called_once_with(
        analyze=analyze_json_str,
        descriptions=[sentinel.desc, sentinel.desc],
    )
    analysis.compile.assert_not_called()
    description.compile.assert_has_calls([call('d1'), call('d2')])


@ctor_patch
def test_given_a_single_value_mapping(ctor, compiler, analysis, description):
    desc = compiler.compile({
        'analyze_as': 'html',
        'descriptions': 'd1',
    })
    assert desc is sentinel.body

    ctor.assert_called_once_with(
        analyze=sentinel.analyze,
        descriptions=[sentinel.desc],
    )
    analysis.compile.assert_called_once_with('html')
    description.compile.assert_called_once_with('d1')


@ctor_patch
def test_given_a_mapping(ctor, compiler, analysis, description):
    desc = compiler.compile({
        'analyze_as': 'text',
        'descriptions': ['d1', 'd2'],
    })
    assert desc is sentinel.body

    ctor.assert_called_once_with(
        analyze=sentinel.analyze,
        descriptions=[sentinel.desc, sentinel.desc],
    )
    analysis.compile.assert_called_once_with('text')
    description.compile.assert_has_calls([call('d1'), call('d2')])


@ctor_patch
def test_given_default(ctor, compiler, analysis, description):
    compiler = compiler.of_default(BodyDescription(
        analyze=sentinel.default_analyze,
        descriptions=[sentinel.default_description],
    ))
    desc = compiler.compile({})
    assert desc is sentinel.body

    ctor.assert_called_once_with(
        analyze=sentinel.default_analyze,
        descriptions=[sentinel.default_description],
    )
    analysis.compile.assert_not_called()
    description.compile.assert_not_called()
