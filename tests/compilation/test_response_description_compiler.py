from unittest.mock import MagicMock, call, sentinel

from pytest import fixture, mark, raises

from preacher.compilation.body import (
    BodyDescriptionCompiler,
    Compiled as BodyCompiled,
)
from preacher.compilation.description import DescriptionCompiler
from preacher.compilation.error import CompilationError, NamedNode
from preacher.compilation.predicate import PredicateCompiler
from preacher.compilation.response import (
    Compiled,
    ResponseDescriptionCompiler,
)


@fixture
def compiler(predicate, description, body):
    return ResponseDescriptionCompiler(
        predicate=predicate,
        description=description,
        body=body,
    )


@fixture
def predicate():
    return MagicMock(
        spec=PredicateCompiler,
        compile=MagicMock(return_value=sentinel.predicate),
    )


@fixture
def description():
    return MagicMock(
        spec=DescriptionCompiler,
        compile=MagicMock(return_value=sentinel.description)
    )


@fixture
def body():
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


def test_given_an_empty_mapping(compiler, predicate, description, body):
    response_description = compiler.compile({}).convert()
    assert response_description.status_code == []
    assert response_description.headers == []
    assert response_description.body is None

    predicate.compile.assert_not_called()
    description.compile.assert_not_called()
    body.compile.assert_not_called()


@mark.parametrize('obj, expected_path', (
    ('', []),
    ({'headers': 'str'}, [NamedNode('headers')]),
))
def test_given_an_invalid_value(obj, expected_path, compiler):
    with raises(CompilationError) as error_info:
        compiler.compile(obj)
    assert error_info.value.path == expected_path


def test_given_simple_values(compiler, predicate, description, body):
    response_description = compiler.compile({
        'status_code': 402,
        'headers': {'k1': 'v1'},
        'body': sentinel.body,
    }).convert()
    assert response_description.status_code == [sentinel.predicate]
    assert response_description.body == sentinel.body_desc
    predicate.compile.assert_called_once_with(402)
    description.compile.assert_called_once_with({'k1': 'v1'})
    body.compile.assert_called_once_with(sentinel.body)


def test_given_filled_values(compiler, predicate, description, body, default):
    response_description = compiler.compile({
        'status_code': [{'k1': 'v1'}, {'k2': 'v2'}],
        'headers': [{'k3': 'v3'}, {'k4': 'v4'}],
        'body': sentinel.body,
    }).convert()
    assert response_description.status_code == [
        sentinel.predicate,
        sentinel.predicate,
    ]
    assert response_description.body == sentinel.body_desc
    predicate.compile.assert_has_calls([
        call({'k1': 'v1'}),
        call({'k2': 'v2'}),
    ])
    description.compile.assert_has_calls([
        call({'k3': 'v3'}),
        call({'k4': 'v4'}),
    ])
    body.compile.assert_called_once_with(sentinel.body)


def test_given_default(compiler, body, default):
    compiler = compiler.of_default(default)
    compiled = compiler.compile({})
    assert compiled == default

    body.of_default.assert_called_once_with(default.body)
