from unittest.mock import MagicMock, call, sentinel

from pytest import fixture, mark, raises

from preacher.compilation.body_description import (
    BodyDescriptionCompiler,
    Compiled as BodyCompiled,
)
from preacher.compilation.description import DescriptionCompiler
from preacher.compilation.error import CompilationError
from preacher.compilation.predicate import PredicateCompiler
from preacher.compilation.response_description import (
    Compiled,
    ResponseDescriptionCompiler,
)


@fixture
def pred_compiler() -> PredicateCompiler:
    return MagicMock(
        spec=PredicateCompiler,
        compile=MagicMock(return_value=sentinel.predicate),
    )


@fixture
def desc_compiler() -> DescriptionCompiler:
    return MagicMock(
        spec=DescriptionCompiler,
        compile=MagicMock(return_value=sentinel.description)
    )


@fixture
def body_desc_compiler() -> BodyDescriptionCompiler:
    compiled = MagicMock(spec=BodyCompiled)
    compiled.convert.return_value = sentinel.body_desc

    compiler = MagicMock(spec=BodyDescriptionCompiler)
    compiler.compile.return_value = compiled
    compiler.of_default.return_value = compiler

    return compiler


@fixture
def default() -> Compiled:
    return Compiled(
        status_code=[sentinel.status_code],
        headers=[sentinel.headers],
        body=sentinel.body,
    )


def test_given_an_empty_mapping(
    pred_compiler,
    desc_compiler,
    body_desc_compiler,
):
    compiler = ResponseDescriptionCompiler(
        predicate_compiler=pred_compiler,
        description_compiler=desc_compiler,
        body_description_compiler=body_desc_compiler,
    )
    response_description = compiler.compile({}).convert()
    assert response_description.status_code_predicates == []
    assert response_description.headers_descriptions == []
    assert response_description.body_description is None

    pred_compiler.compile.assert_not_called()
    desc_compiler.compile.assert_not_called()
    body_desc_compiler.compile.assert_not_called()


@mark.parametrize('obj, error_suffix', (
    ('', ''),
    ({'headers': 'str'}, ': headers'),
    ({'body': 'str'}, ': body'),
    ({'body': ['str']}, ': body.descriptions[0]'),
))
def test_given_an_invalid_value(obj, error_suffix):
    compiler = ResponseDescriptionCompiler()
    with raises(CompilationError) as error_info:
        compiler.compile(obj)
    assert str(error_info.value).endswith(error_suffix)


def test_given_simple_values(pred_compiler, desc_compiler, body_desc_compiler):
    compiler = ResponseDescriptionCompiler(
        predicate_compiler=pred_compiler,
        description_compiler=desc_compiler,
        body_description_compiler=body_desc_compiler,
    )
    response_description = compiler.compile({
        'status_code': 402,
        'headers': {'k1': 'v1'},
        'body': sentinel.body,
    }).convert()
    assert response_description.status_code_predicates == [sentinel.predicate]
    assert response_description.body_description == sentinel.body_desc
    pred_compiler.compile.assert_called_once_with(402)
    desc_compiler.compile.assert_called_once_with({'k1': 'v1'})
    body_desc_compiler.compile.assert_called_once_with(sentinel.body)


def test_given_filled_values(
    pred_compiler,
    desc_compiler,
    body_desc_compiler,
    default,
):
    compiler = ResponseDescriptionCompiler(
        predicate_compiler=pred_compiler,
        description_compiler=desc_compiler,
        body_description_compiler=body_desc_compiler,
    ).of_default(default)
    response_description = compiler.compile({
        'status_code': [{'k1': 'v1'}, {'k2': 'v2'}],
        'headers': [{'k3': 'v3'}, {'k4': 'v4'}],
        'body': sentinel.body,
    }).convert()
    assert response_description.status_code_predicates == [
        sentinel.predicate,
        sentinel.predicate,
    ]
    assert response_description.body_description == sentinel.body_desc
    pred_compiler.compile.assert_has_calls([
        call({'k1': 'v1'}),
        call({'k2': 'v2'}),
    ])
    desc_compiler.compile.assert_has_calls([
        call({'k3': 'v3'}),
        call({'k4': 'v4'}),
    ])
    body_desc_compiler.compile.assert_called_once_with(sentinel.body)


def test_given_default(
    pred_compiler,
    desc_compiler,
    body_desc_compiler,
    default,
):
    compiler = ResponseDescriptionCompiler(
        predicate_compiler=pred_compiler,
        description_compiler=desc_compiler,
        body_description_compiler=body_desc_compiler,
    ).of_default(default)
    compiled = compiler.compile({})
    assert compiled == default

    body_desc_compiler.of_default.assert_called_once_with(default.body)
