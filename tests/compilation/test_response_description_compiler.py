from unittest.mock import ANY, NonCallableMock, call, sentinel

from pytest import fixture, mark, raises

from preacher.compilation.description import DescriptionCompiler
from preacher.compilation.error import CompilationError, NamedNode
from preacher.compilation.predicate import PredicateCompiler
from preacher.compilation.response import ResponseDescriptionCompiler
from preacher.compilation.response_body import (
    ResponseBodyDescriptionCompiled,
    ResponseBodyDescriptionCompiler,
)

PKG = 'preacher.compilation.response'


@fixture
def compiler(predicate, description, body) -> ResponseDescriptionCompiler:
    return ResponseDescriptionCompiler(
        predicate=predicate,
        description=description,
        body=body,
    )


@fixture
def predicate():
    compiler = NonCallableMock(PredicateCompiler)
    compiler.compile.return_value = sentinel.predicate
    return compiler


@fixture
def description():
    compiler = NonCallableMock(DescriptionCompiler)
    compiler.compile.return_value = sentinel.description
    return compiler


@fixture
def body(body_of_default):
    compiler = NonCallableMock(ResponseBodyDescriptionCompiler)
    compiler.compile.return_value = sentinel.body_desc
    compiler.of_default.return_value = body_of_default
    return compiler


@fixture
def body_of_default():
    compiler = NonCallableMock(ResponseBodyDescriptionCompiler)
    compiler.compile.return_value = sentinel.sub_body_desc
    return compiler


@mark.parametrize(('obj', 'expected_path'), (
    ('', []),
    ({'headers': 'str'}, [NamedNode('headers')]),
))
def test_given_an_invalid_value(obj, expected_path, compiler):
    with raises(CompilationError) as error_info:
        compiler.compile(obj)
    assert error_info.value.path == expected_path


def test_given_an_empty_mapping(compiler, predicate, description, body):
    compiled = compiler.compile({})
    assert compiled.status_code is None
    assert compiled.headers is None
    assert compiled.body is None

    predicate.compile.assert_not_called()
    description.compile.assert_not_called()
    body.compile.assert_not_called()


def test_given_simple_values(compiler, predicate, description, body):
    compiled = compiler.compile({
        'status_code': 402,
        'headers': {'k1': 'v1'},
        'body': sentinel.body,
    })
    assert compiled.status_code == [sentinel.predicate]
    assert compiled.headers == [sentinel.description]
    assert compiled.body == sentinel.body_desc

    predicate.compile.assert_called_once_with(402)
    description.compile.assert_called_once_with({'k1': 'v1'})
    body.compile.assert_called_once_with(sentinel.body)


def test_given_filled_values(compiler, predicate, description, body):
    compiled = compiler.compile({
        'status_code': [{'k1': 'v1'}, {'k2': 'v2'}],
        'headers': [{'k3': 'v3'}, {'k4': 'v4'}],
        'body': sentinel.body,
    })
    assert compiled.status_code == [sentinel.predicate, sentinel.predicate]
    assert compiled.headers == [sentinel.description, sentinel.description]
    assert compiled.body == sentinel.body_desc

    predicate.compile.assert_has_calls([
        call({'k1': 'v1'}),
        call({'k2': 'v2'}),
    ])
    description.compile.assert_has_calls([
        call({'k3': 'v3'}),
        call({'k4': 'v4'}),
    ])
    body.compile.assert_called_once_with(sentinel.body)


@fixture
def initial_default():
    initial_default = NonCallableMock(ResponseBodyDescriptionCompiled)
    initial_default.replace.return_value = sentinel.new_default
    return initial_default


def test_given_hollow_default(
    mocker,
    predicate,
    description,
    body,
    initial_default,
):
    compiler_ctor = mocker.patch(f'{PKG}.ResponseDescriptionCompiler')
    compiler_ctor.return_value = sentinel.compiler_of_default

    compiler = ResponseDescriptionCompiler(
        predicate=predicate,
        description=description,
        body=body,
        default=initial_default,
    )

    default = NonCallableMock(ResponseBodyDescriptionCompiled, body=None)
    compiler_of_default = compiler.of_default(default)
    assert compiler_of_default is sentinel.compiler_of_default

    body.of_default.assert_not_called()
    initial_default.replace.assert_called_once_with(default)
    compiler_ctor.assert_called_once_with(
        predicate=predicate,
        description=description,
        body=body,
        default=ANY,
    )
    default = compiler_ctor.call_args[1]['default']
    assert default is sentinel.new_default


def test_given_filled_default(
    mocker,
    predicate,
    description,
    body,
    body_of_default,
    initial_default,
):
    compiler_ctor = mocker.patch(f'{PKG}.ResponseDescriptionCompiler')
    compiler_ctor.return_value = sentinel.compiler_of_default

    compiler = ResponseDescriptionCompiler(
        predicate=predicate,
        description=description,
        body=body,
        default=initial_default,
    )

    default = NonCallableMock(ResponseBodyDescriptionCompiled)
    default.body = sentinel.default_body
    compiler_of_default = compiler.of_default(default)
    assert compiler_of_default is sentinel.compiler_of_default

    body.of_default.assert_called_once_with(sentinel.default_body)
    initial_default.replace.assert_called_once_with(default)
    compiler_ctor.assert_called_once_with(
        predicate=predicate,
        description=description,
        body=body_of_default,
        default=ANY,
    )
    default = compiler_ctor.call_args[1]['default']
    assert default is sentinel.new_default
