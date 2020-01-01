from unittest.mock import MagicMock, call, sentinel, patch

from pytest import fixture, mark, raises

from preacher.compilation.body import (
    BodyDescriptionCompiler,
    Compiled as BodyCompiled,
)
from preacher.compilation.description import DescriptionCompiler
from preacher.compilation.error import CompilationError, NamedNode
from preacher.compilation.predicate import PredicateCompiler
from preacher.compilation.response import ResponseDescriptionCompiler

ctor_patch = patch(
    'preacher.compilation.response.ResponseDescription',
    return_value=sentinel.response,
)


@fixture
def compiler(predicate, description, body) -> ResponseDescriptionCompiler:
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
def body(body_of_default):
    compiled = MagicMock(spec=BodyCompiled)
    compiled.convert.return_value = sentinel.body_desc

    compiler = MagicMock(spec=BodyDescriptionCompiler)
    compiler.compile.return_value = compiled
    compiler.of_default.return_value = body_of_default

    return compiler


@fixture
def body_of_default():
    compiled = MagicMock(spec=BodyCompiled)
    compiled.convert.return_value = sentinel.sub_body_desc

    compiler = MagicMock(spec=BodyDescriptionCompiler)
    compiler.compile.return_value = compiled
    return compiler


@ctor_patch
def test_given_an_empty_mapping(ctor, compiler, predicate, description, body):
    response = compiler.compile({})
    assert response is sentinel.response

    ctor.assert_called_once_with(
        status_code=[],
        headers=[],
        body=sentinel.body_desc
    )
    predicate.compile.assert_not_called()
    description.compile.assert_not_called()
    body.compile.assert_called_once_with({})


@mark.parametrize('obj, expected_path', (
    ('', []),
    ({'headers': 'str'}, [NamedNode('headers')]),
))
def test_given_an_invalid_value(obj, expected_path, compiler):
    with raises(CompilationError) as error_info:
        compiler.compile(obj)
    assert error_info.value.path == expected_path


@ctor_patch
def test_given_simple_values(ctor, compiler, predicate, description, body):
    response = compiler.compile({
        'status_code': 402,
        'headers': {'k1': 'v1'},
        'body': sentinel.body,
    })
    assert response is sentinel.response

    ctor.assert_called_once_with(
        status_code=[sentinel.predicate],
        headers=[sentinel.description],
        body=sentinel.body_desc,
    )
    predicate.compile.assert_called_once_with(402)
    description.compile.assert_called_once_with({'k1': 'v1'})
    body.compile.assert_called_once_with(sentinel.body)


@ctor_patch
def test_given_filled_values(ctor, compiler, predicate, description, body):
    response = compiler.compile({
        'status_code': [{'k1': 'v1'}, {'k2': 'v2'}],
        'headers': [{'k3': 'v3'}, {'k4': 'v4'}],
        'body': sentinel.body,
    })
    assert response is sentinel.response

    ctor.assert_called_once_with(
        status_code=[sentinel.predicate, sentinel.predicate],
        headers=[sentinel.description, sentinel.description],
        body=sentinel.body_desc,
    )
    predicate.compile.assert_has_calls([
        call({'k1': 'v1'}),
        call({'k2': 'v2'}),
    ])
    description.compile.assert_has_calls([
        call({'k3': 'v3'}),
        call({'k4': 'v4'}),
    ])
    body.compile.assert_called_once_with(sentinel.body)


@ctor_patch
def test_given_default(
    ctor,
    compiler,
    predicate,
    description,
    body,
    body_of_default,
):
    compiler = compiler.of_default({
        'status_code': 200,
        'headers': {},
        'body': sentinel.body,
    })
    response = compiler.compile({})
    assert response is sentinel.response

    ctor.assert_called_once_with(
        status_code=[sentinel.predicate],
        headers=[sentinel.description],
        body=sentinel.sub_body_desc,
    )
    predicate.compile.assert_called_once_with(200)
    description.compile.assert_called_once_with({})
    body.compile.assert_called_once_with(sentinel.body)
    body.of_default.assert_called_once()
    body_of_default.compile.assert_called_once_with({})
