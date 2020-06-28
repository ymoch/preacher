from unittest.mock import Mock, NonCallableMock, sentinel

from pytest import fixture, mark, raises

from preacher.compilation.error import CompilationError, NamedNode
from preacher.compilation.request_body import (
    RequestBodyCompiler,
    RequestBodyCompiled,
    UrlencodedRequestBodyCompiled,
    JsonRequestBodyCompiled,
)

PACKAGE = 'preacher.compilation.request_body'


@fixture
def default_body():
    default = NonCallableMock(RequestBodyCompiled)
    default.compile_and_replace = Mock(return_value=sentinel.default_result)
    return default


@fixture
def compiler(default_body):
    return RequestBodyCompiler(default=default_body)


@mark.parametrize(('obj', 'expected_path'), [
    ([], []),
    ({'type': 1}, [NamedNode('type')]),
    ({'type': 'invalid'}, [NamedNode('type')]),
])
def test_compile_given_invalid_obj(compiler, obj, expected_path):
    with raises(CompilationError) as error_info:
        compiler.compile(obj)
    assert error_info.value.path == expected_path


def test_compile_empty(compiler, default_body):
    compiled = compiler.compile({})
    assert compiled is sentinel.default_result


@mark.parametrize(('type_key', 'expected_replacer'), [
    ('urlencoded', UrlencodedRequestBodyCompiled()),
    ('json', JsonRequestBodyCompiled()),
])
def test_given_type(compiler, default_body, type_key, expected_replacer):
    replaced_body = NonCallableMock(RequestBodyCompiled)
    replaced_body.compile_and_replace = Mock(return_value=sentinel.new_result)
    default_body.replace = Mock(return_value=replaced_body)

    obj = {'type': type_key, 'foo': 'bar'}
    compiled = compiler.compile(obj)
    assert compiled is sentinel.new_result

    default_body.replace.assert_called_once_with(expected_replacer)
    replaced_body.compile_and_replace.assert_called_once_with(obj)


def test_of_default(compiler: RequestBodyCompiler, default_body, mocker):
    default_body.replace = Mock(return_value=sentinel.new_default_body)

    ctor = mocker.patch(f'{PACKAGE}.RequestBodyCompiler')
    ctor.return_value = sentinel.new_compiler

    new_compiler = compiler.of_default(sentinel.new_default_body)
    assert new_compiler is sentinel.new_compiler

    ctor.assert_called_once_with(default=sentinel.new_default_body)
    default_body.replace.assert_called_once_with(sentinel.new_default_body)
