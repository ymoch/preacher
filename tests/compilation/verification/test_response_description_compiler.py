from unittest.mock import ANY, NonCallableMock, call, sentinel

from pytest import fixture, mark, raises

from preacher.compilation.error import CompilationError, NamedNode
from preacher.compilation.verification.description import DescriptionCompiler
from preacher.compilation.verification.predicate import PredicateCompiler
from preacher.compilation.verification.response import ResponseDescriptionCompiled
from preacher.compilation.verification.response import ResponseDescriptionCompiler
from preacher.compilation.verification.response_body import ResponseBodyDescriptionCompiled

PKG = 'preacher.compilation.verification.response'


@fixture
def compiler(predicate, description) -> ResponseDescriptionCompiler:
    return ResponseDescriptionCompiler(predicate=predicate, description=description)


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


@mark.parametrize(('obj', 'expected_path'), (
    ('', []),
    ({'headers': 'str'}, [NamedNode('headers')]),
    ({'body': 'str'}, [NamedNode('body')]),
))
def test_given_an_invalid_value(obj, expected_path, compiler):
    with raises(CompilationError) as error_info:
        compiler.compile(obj)
    assert error_info.value.path == expected_path


def test_given_an_empty_mapping(compiler, predicate, description):
    compiled = compiler.compile({})
    assert compiled.status_code is None
    assert compiled.headers is None
    assert compiled.body is None

    predicate.compile.assert_not_called()
    description.compile.assert_not_called()


def test_given_simple_values(compiler, predicate, description):
    compiled = compiler.compile({
        'status_code': 402,
        'headers': {'k1': 'v1'},
        'body': {'k2': 'v2'},
    })
    assert compiled.status_code == [sentinel.predicate]
    assert compiled.headers == [sentinel.description]
    assert compiled.body == [sentinel.description]

    predicate.compile.assert_called_once_with(402)
    description.compile.assert_has_calls([call({'k1': 'v1'}), call({'k2': 'v2'})])


def test_given_filled_values(compiler, predicate, description):
    compiled = compiler.compile({
        'status_code': [{'k1': 'v1'}, {'k2': 'v2'}],
        'headers': [{'k3': 'v3'}, {'k4': 'v4'}],
        'body': [{'k5': 'v5'}, {'k6': 'v6'}],
    })
    assert compiled.status_code == [sentinel.predicate, sentinel.predicate]
    assert compiled.headers == [sentinel.description, sentinel.description]
    assert compiled.body == [sentinel.description, sentinel.description]

    predicate.compile.assert_has_calls([
        call({'k1': 'v1'}),
        call({'k2': 'v2'}),
    ])
    description.compile.assert_has_calls([
        call({'k3': 'v3'}),
        call({'k4': 'v4'}),
        call({'k5': 'v5'}),
        call({'k6': 'v6'}),
    ])


@fixture
def initial_default():
    initial_default = NonCallableMock(ResponseDescriptionCompiled)
    initial_default.replace.return_value = sentinel.new_default
    return initial_default


def test_given_hollow_default(mocker, predicate, description, initial_default):
    compiler_ctor = mocker.patch(f'{PKG}.ResponseDescriptionCompiler')
    compiler_ctor.return_value = sentinel.compiler_of_default

    compiler = ResponseDescriptionCompiler(
        predicate=predicate,
        description=description,
        default=initial_default,
    )

    default = NonCallableMock(ResponseBodyDescriptionCompiled, body=None)
    compiler_of_default = compiler.of_default(default)
    assert compiler_of_default is sentinel.compiler_of_default

    initial_default.replace.assert_called_once_with(default)
    compiler_ctor.assert_called_once_with(
        predicate=predicate,
        description=description,
        default=ANY,
    )
    default = compiler_ctor.call_args[1]['default']
    assert default is sentinel.new_default


def test_given_filled_default(mocker, predicate, description, initial_default):
    compiler_ctor = mocker.patch(f'{PKG}.ResponseDescriptionCompiler')
    compiler_ctor.return_value = sentinel.compiler_of_default

    compiler = ResponseDescriptionCompiler(
        predicate=predicate,
        description=description,
        default=initial_default,
    )

    default = NonCallableMock(ResponseBodyDescriptionCompiled)
    default.body = sentinel.default_body
    compiler_of_default = compiler.of_default(default)
    assert compiler_of_default is sentinel.compiler_of_default

    initial_default.replace.assert_called_once_with(default)
    compiler_ctor.assert_called_once_with(
        predicate=predicate,
        description=description,
        default=ANY,
    )
    default = compiler_ctor.call_args[1]['default']
    assert default is sentinel.new_default
