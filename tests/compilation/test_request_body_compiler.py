from unittest.mock import NonCallableMock

from pytest import fixture, raises

from preacher.compilation.request_body import (
    RequestBodyCompiled,
    RequestBodyCompiler,
)


@fixture
def compiler() -> RequestBodyCompiler:
    return RequestBodyCompiler()


def test_compile(compiler: RequestBodyCompiler):
    with raises(NotImplementedError):
        compiler.compile({})


def test_of_default(compiler: RequestBodyCompiler):
    default = NonCallableMock(RequestBodyCompiled)
    new_compiler = compiler.of_default(default)
    assert new_compiler is compiler
