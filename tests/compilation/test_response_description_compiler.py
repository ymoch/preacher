from unittest.mock import MagicMock, call, sentinel

from pytest import fixture, mark, raises

from preacher.compilation.description import DescriptionCompiler
from preacher.compilation.error import CompilationError
from preacher.compilation.predicate import PredicateCompiler
from preacher.compilation.response_description import (
    ResponseDescriptionCompiler,
)


@fixture
def predicate_compiler() -> PredicateCompiler:
    return MagicMock(
        spec=PredicateCompiler,
        compile=MagicMock(return_value=sentinel.predicate),
    )


@fixture
def description_compiler() -> DescriptionCompiler:
    return MagicMock(
        spec=DescriptionCompiler,
        compile=MagicMock(return_value=sentinel.description),
    )


def test_given_an_empty_mapping(predicate_compiler, description_compiler):
    compiler = ResponseDescriptionCompiler(
        predicate_compiler=predicate_compiler,
        description_compiler=description_compiler,
    )
    response_description = compiler.compile({})
    assert response_description.status_code_predicates == []
    assert response_description.headers_descriptions == []
    assert response_description.body_descriptions == []

    predicate_compiler.compile.assert_not_called()
    description_compiler.compile.assert_not_called()


@mark.parametrize('obj, error_suffix', (
    ('', ''),
    ({'headers': 'str'}, ': headers'),
    ({'headers': ['str']}, ': headers[0]'),
    ({'body': 'str'}, ': body'),
    ({'body': ['str']}, ': body[0]'),
))
def test_given_an_invalid_value(obj, error_suffix):
    compiler = ResponseDescriptionCompiler()
    with raises(CompilationError) as error_info:
        compiler.compile(obj)
    assert str(error_info.value).endswith(error_suffix)


def test_given_simple_values(predicate_compiler, description_compiler):
    compiler = ResponseDescriptionCompiler(
        predicate_compiler=predicate_compiler,
        description_compiler=description_compiler,
    )
    response_description = compiler.compile({
        'status_code': 402,
        'headers': {'k1': 'v1'},
        'body': {'k2': 'v2'},
    })
    assert response_description.status_code_predicates == [sentinel.predicate]
    assert response_description.body_descriptions == [sentinel.description]
    predicate_compiler.compile.assert_called_once_with(402)
    description_compiler.compile.assert_has_calls((
        call({'k1': 'v1'}),
        call({'k2': 'v2'}),
    ))


def test_given_fill_values(predicate_compiler, description_compiler):
    compiler = ResponseDescriptionCompiler(
        predicate_compiler=predicate_compiler,
        description_compiler=description_compiler,
    )
    response_description = compiler.compile({
        'status_code': [{'be_greater_than': 0}, {'be_less_than': 400}],
        'body': [{'key1': 'value1'}, {'key2': 'value2'}],
    })
    assert response_description.status_code_predicates == [
        sentinel.predicate,
        sentinel.predicate,
    ]
    assert response_description.body_descriptions == [
        sentinel.description,
        sentinel.description,
    ]
    predicate_compiler.compile.assert_has_calls([
        call({'be_greater_than': 0}),
        call({'be_less_than': 400}),
    ])
    description_compiler.compile.assert_has_calls([
        call({'key1': 'value1'}),
        call({'key2': 'value2'}),
    ])
