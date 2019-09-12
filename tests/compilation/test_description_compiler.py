from unittest.mock import MagicMock, call, sentinel

from pytest import fixture, raises

from preacher.compilation.extraction import ExtractionCompiler
from preacher.compilation.predicate import PredicateCompiler
from preacher.compilation.description import DescriptionCompiler
from preacher.compilation.error import CompilationError


@fixture
def extraction_compiler() -> ExtractionCompiler:
    return MagicMock(
        spec=ExtractionCompiler,
        compile=MagicMock(return_value=sentinel.extractor),
    )


@fixture
def predicate_compiler() -> PredicateCompiler:
    return MagicMock(
        spec=PredicateCompiler,
        compile=MagicMock(return_value=sentinel.predicate),
    )


def test_given_an_empty_mapping():
    compiler = DescriptionCompiler()
    with raises(CompilationError) as error_info:
        compiler.compile({})
    assert str(error_info.value).startswith('Description.describe')


def test_given_a_string_predicate(extraction_compiler, predicate_compiler):
    compiler = DescriptionCompiler(
        extraction_compiler=extraction_compiler,
        predicate_compiler=predicate_compiler,
    )
    description = compiler.compile({
        'describe': 'foo',
        'should': 'string',
    })
    assert description.extractor == sentinel.extractor
    assert description.predicates == [sentinel.predicate]

    extraction_compiler.compile.assert_called_with('foo')
    predicate_compiler.compile.assert_called_once_with('string')


def test_given_a_mapping_predicate(extraction_compiler, predicate_compiler):
    compiler = DescriptionCompiler(
        extraction_compiler=extraction_compiler,
        predicate_compiler=predicate_compiler,
    )
    description = compiler.compile({
        'describe': 'foo',
        'should': {'key': 'value'}
    })
    assert description.extractor == sentinel.extractor
    assert description.predicates == [sentinel.predicate]

    extraction_compiler.compile.assert_called_once_with('foo')
    predicate_compiler.compile.assert_called_once_with({'key': 'value'})


def test_given_a_list_of_mapping_predicates(
    extraction_compiler,
    predicate_compiler,
):
    compiler = DescriptionCompiler(
        extraction_compiler=extraction_compiler,
        predicate_compiler=predicate_compiler,
    )
    description = compiler.compile({
        'describe': {'key': 'value'},
        'should': [{'key1': 'value1'}, {'key2': 'value2'}]
    })
    assert description.extractor == sentinel.extractor
    assert description.predicates == [sentinel.predicate, sentinel.predicate]

    extraction_compiler.compile.assert_called_once_with({'key': 'value'})
    predicate_compiler.compile.assert_has_calls([
        call({'key1': 'value1'}),
        call({'key2': 'value2'}),
    ])
