from unittest.mock import MagicMock, call, sentinel

from pytest import fixture, mark

from preacher.compilation.analysis import AnalysisCompiler
from preacher.compilation.body_description import BodyDescriptionCompiler
from preacher.compilation.description import DescriptionCompiler
from preacher.compilation.error import CompilationError


@fixture
def analysis_compiler():
    return MagicMock(
        spec=AnalysisCompiler,
        compile=MagicMock(return_value=sentinel.analyze),
    )


@fixture
def desc_compiler():
    return MagicMock(
        spec=DescriptionCompiler,
        compile=MagicMock(return_value=sentinel.desc),
    )


@mark.xfail(raises=CompilationError)
@mark.parametrize('value', (None, 0, ''))
def test_given_invalid_values(value):
    BodyDescriptionCompiler().compile(value)


@mark.parametrize('value', ([],))
def test_given_empty_values(value, analysis_compiler, desc_compiler):
    compiler = BodyDescriptionCompiler(
        analysis_compiler=analysis_compiler,
        description_compiler=desc_compiler,
    )
    desc = compiler.compile(value).convert()
    assert desc.descriptions == []

    analysis_compiler.compile.assert_not_called()
    desc_compiler.compile.assert_not_called()


def test_given_a_list(analysis_compiler, desc_compiler):
    compiler = BodyDescriptionCompiler(
        analysis_compiler=analysis_compiler,
        description_compiler=desc_compiler,
    )
    desc = compiler.compile(['d1', 'd2']).convert()
    assert desc.descriptions == [sentinel.desc, sentinel.desc]

    analysis_compiler.compile.assert_not_called()
    desc_compiler.compile.assert_has_calls([call('d1'), call('d2')])


def test_given_a_mapping_of_single_value(analysis_compiler, desc_compiler):
    compiler = BodyDescriptionCompiler(
        analysis_compiler=analysis_compiler,
        description_compiler=desc_compiler,
    )
    desc = compiler.compile(
        {'analyze_as': 'html', 'descriptions': 'd1'}
    ).convert()
    assert desc.descriptions == [sentinel.desc]

    analysis_compiler.compile.assert_called_once_with('html')
    desc_compiler.compile.assert_called_once_with('d1')


def test_given_a_mapping(analysis_compiler, desc_compiler):
    compiler = BodyDescriptionCompiler(
        analysis_compiler=analysis_compiler,
        description_compiler=desc_compiler,
    )
    desc = compiler.compile(
        {'analyze_as': 'text', 'descriptions': ['d1', 'd2']}
    ).convert()
    assert desc.descriptions == [sentinel.desc, sentinel.desc]

    analysis_compiler.compile.assert_called_once_with('text')
    desc_compiler.compile.assert_has_calls([call('d1'), call('d2')])
