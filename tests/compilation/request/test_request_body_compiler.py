from unittest.mock import Mock, NonCallableMock, sentinel

from pytest import fixture, mark, raises

from preacher.compilation.argument import Argument
from preacher.compilation.error import CompilationError, NamedNode
from preacher.compilation.request.request_body import JsonRequestBodyCompiled
from preacher.compilation.request.request_body import RequestBodyCompiled
from preacher.compilation.request.request_body import RequestBodyCompiler
from preacher.compilation.request.request_body import UrlencodedRequestBodyCompiled

PKG = "preacher.compilation.request.request_body"


@fixture
def default_body():
    default = NonCallableMock(RequestBodyCompiled)
    default.compile_and_replace = Mock(return_value=sentinel.default_result)
    return default


@fixture
def compiler(default_body) -> RequestBodyCompiler:
    return RequestBodyCompiler(default=default_body)


@mark.parametrize(
    ("obj", "expected_path"),
    (
        ([], []),
        ({"type": 1}, [NamedNode("type")]),
        ({"type": "invalid"}, [NamedNode("type")]),
    ),
)
def test_compile_given_invalid_obj(compiler, obj, expected_path):
    with raises(CompilationError) as error_info:
        compiler.compile(obj)
    assert error_info.value.path == expected_path


def test_compile_empty(compiler, default_body):
    compiled = compiler.compile({})
    assert compiled is sentinel.default_result


@mark.parametrize(
    ("type_key", "expected"),
    (
        ("urlencoded", UrlencodedRequestBodyCompiled()),
        ("json", JsonRequestBodyCompiled()),
    ),
)
def test_given_type(compiler: RequestBodyCompiler, default_body, type_key, expected):
    replaced_body = NonCallableMock(RequestBodyCompiled)
    replaced_body.compile_and_replace = Mock(return_value=sentinel.new_result)
    default_body.replace = Mock(return_value=replaced_body)

    obj = {"type": Argument("type"), "foo": Argument("foo")}
    compiled = compiler.compile(obj, {"type": type_key, "foo": "bar"})
    assert compiled is sentinel.new_result

    default_body.replace.assert_called_once_with(expected)
    replaced_body.compile_and_replace.assert_called_once_with({"type": type_key, "foo": "bar"})


def test_of_default(compiler: RequestBodyCompiler, default_body, mocker):
    default_body.replace = Mock(return_value=sentinel.new_default_body)

    ctor = mocker.patch(f"{PKG}.RequestBodyCompiler")
    ctor.return_value = sentinel.new_compiler

    new_compiler = compiler.of_default(sentinel.new_default_body)
    assert new_compiler is sentinel.new_compiler

    ctor.assert_called_once_with(default=sentinel.new_default_body)
    default_body.replace.assert_called_once_with(sentinel.new_default_body)
