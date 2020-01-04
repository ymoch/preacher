from unittest.mock import ANY, MagicMock, call, sentinel, patch

from pytest import fixture, mark, raises

from preacher.compilation.analysis import AnalysisCompiler
from preacher.compilation.body import (
    BodyDescriptionCompiled,
    BodyDescriptionCompiler,
)
from preacher.compilation.description import DescriptionCompiler
from preacher.compilation.error import CompilationError
from preacher.core.body import BodyDescription

PACKAGE = 'preacher.compilation.body'


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


def test_given_empty_object(compiler, analysis, description):
    body = compiler.compile({})
    assert body.analyze is None
    assert body.descriptions is None

    analysis.compile.assert_not_called()
    description.compile.assert_not_called()


def test_given_an_empty_list(compiler, analysis, description):
    body = compiler.compile([])
    assert body.analyze is None
    assert body.descriptions == []

    analysis.compile.assert_not_called()
    description.compile.assert_not_called()


def test_given_a_list(compiler, analysis, description):
    body = compiler.compile(['d1', 'd2'])
    assert body.analyze is None
    assert body.descriptions == [sentinel.desc, sentinel.desc]

    analysis.compile.assert_not_called()
    description.compile.assert_has_calls([call('d1'), call('d2')])


def test_given_a_single_value_mapping(compiler, analysis, description):
    body = compiler.compile({
        'analyze_as': 'html',
        'descriptions': 'd1',
    })
    assert body.analyze is sentinel.analyze
    assert body.descriptions == [sentinel.desc]

    analysis.compile.assert_called_once_with('html')
    description.compile.assert_called_once_with('d1')


def test_given_a_mapping(compiler, analysis, description):
    body = compiler.compile({
        'analyze_as': 'text',
        'descriptions': ['d1', 'd2'],
    })
    assert body.analyze is sentinel.analyze
    assert body.descriptions == [sentinel.desc, sentinel.desc]

    analysis.compile.assert_called_once_with('text')
    description.compile.assert_has_calls([call('d1'), call('d2')])


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


@patch(
    target=f'{PACKAGE}.BodyDescriptionCompiler',
    return_value=sentinel.compiler_of_default,
)
def test_of_default(compiler_ctor, compiler, analysis, description):
    initial_default = MagicMock(BodyDescriptionCompiled)
    initial_default.replace.return_value = sentinel.new_default

    compiler = BodyDescriptionCompiler(analysis, description, initial_default)
    compiler_of_default = compiler.of_default(sentinel.default)
    assert compiler_of_default is sentinel.compiler_of_default

    initial_default.replace.assert_called_once_with(sentinel.default)

    compiler_ctor.assert_called_once_with(
        analysis=analysis,
        description=description,
        default=ANY,
    )
    default = compiler_ctor.call_args[1]['default']
    assert default is sentinel.new_default
