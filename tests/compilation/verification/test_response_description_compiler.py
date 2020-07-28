from unittest.mock import NonCallableMock, call, sentinel

from pytest import fixture, mark, raises

from preacher.compilation.error import CompilationError
from preacher.compilation.verification.description import DescriptionCompiler
from preacher.compilation.verification.predicate import PredicateCompiler
from preacher.compilation.verification.response import ResponseDescriptionCompiled
from preacher.compilation.verification.response import ResponseDescriptionCompiler

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
        'status_code': sentinel.status_code,
        'headers': sentinel.headers,
        'body': sentinel.body,
    })
    assert compiled.status_code == [sentinel.predicate]
    assert compiled.headers == [sentinel.description]
    assert compiled.body == [sentinel.description]

    predicate.compile.assert_called_once_with(sentinel.status_code)
    description.compile.assert_has_calls([call(sentinel.headers), call(sentinel.body)])


def test_given_filled_values(compiler, predicate, description):
    compiled = compiler.compile({
        'status_code': [sentinel.status_code_1, sentinel.status_code_2],
        'headers': [sentinel.headers_1, sentinel.headers_2],
        'body': [sentinel.body_1, sentinel.body_2],
    })
    assert compiled.status_code == [sentinel.predicate, sentinel.predicate]
    assert compiled.headers == [sentinel.description, sentinel.description]
    assert compiled.body == [sentinel.description, sentinel.description]

    predicate.compile.assert_has_calls([
        call(sentinel.status_code_1),
        call(sentinel.status_code_2),
    ])
    description.compile.assert_has_calls([
        call(sentinel.headers_1),
        call(sentinel.headers_2),
        call(sentinel.body_1),
        call(sentinel.body_2),
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

    default = NonCallableMock(ResponseDescriptionCompiled, body=None)
    compiler_of_default = compiler.of_default(default)
    assert compiler_of_default is sentinel.compiler_of_default

    initial_default.replace.assert_called_once_with(default)
    compiler_ctor.assert_called_once_with(
        predicate=predicate,
        description=description,
        default=sentinel.new_default,
    )


def test_given_filled_default(mocker, predicate, description, initial_default):
    compiler_ctor = mocker.patch(f'{PKG}.ResponseDescriptionCompiler')
    compiler_ctor.return_value = sentinel.compiler_of_default

    compiler = ResponseDescriptionCompiler(
        predicate=predicate,
        description=description,
        default=initial_default,
    )

    default = NonCallableMock(ResponseDescriptionCompiled)
    compiler_of_default = compiler.of_default(default)
    assert compiler_of_default is sentinel.compiler_of_default

    initial_default.replace.assert_called_once_with(default)
    compiler_ctor.assert_called_once_with(
        predicate=predicate,
        description=description,
        default=sentinel.new_default,
    )
