from unittest.mock import ANY, Mock, NonCallableMock, call, sentinel

from pytest import fixture, mark, raises

from preacher.compilation.error import CompilationError
from preacher.compilation.verification.description import DescriptionCompiler
from preacher.compilation.verification.response_body import ResponseBodyDescriptionCompiled
from preacher.compilation.verification.response_body import ResponseBodyDescriptionCompiler

PKG = 'preacher.compilation.verification.response_body'


@fixture
def compiler(description) -> ResponseBodyDescriptionCompiler:
    return ResponseBodyDescriptionCompiler(description)


@fixture
def description():
    return NonCallableMock(DescriptionCompiler, compile=Mock(return_value=sentinel.desc))


@mark.parametrize('value', (None, 0, ''))
def test_given_invalid_values(compiler, value):
    with raises(CompilationError):
        compiler.compile(value)


def test_given_empty_object(compiler, description):
    body = compiler.compile({})
    assert body.descriptions is None

    description.compile.assert_not_called()


def test_given_an_empty_list(compiler, description):
    body = compiler.compile([])
    assert body.descriptions == []

    description.compile.assert_not_called()


def test_given_a_list(compiler, description):
    body = compiler.compile(['d1', 'd2'])
    assert body.descriptions == [sentinel.desc, sentinel.desc]

    description.compile.assert_has_calls([call('d1'), call('d2')])


def test_given_a_single_value_mapping(compiler, description):
    body = compiler.compile({'descriptions': 'd1'})
    assert body.descriptions == [sentinel.desc]

    description.compile.assert_called_once_with('d1')


def test_given_a_mapping(compiler, description):
    body = compiler.compile({'descriptions': ['d1', 'd2']})
    assert body.descriptions == [sentinel.desc, sentinel.desc]

    description.compile.assert_has_calls([call('d1'), call('d2')])


def test_of_default(mocker, description):
    compiler_ctor = mocker.patch(f'{PKG}.ResponseBodyDescriptionCompiler')
    compiler_ctor.return_value = sentinel.compiler_of_default

    initial_default = NonCallableMock(ResponseBodyDescriptionCompiled)
    initial_default.replace.return_value = sentinel.new_default

    compiler = ResponseBodyDescriptionCompiler(description=description, default=initial_default)
    compiler_of_default = compiler.of_default(sentinel.default)
    assert compiler_of_default is sentinel.compiler_of_default

    initial_default.replace.assert_called_once_with(sentinel.default)

    compiler_ctor.assert_called_once_with(description=description, default=ANY)
    default = compiler_ctor.call_args[1]['default']
    assert default is sentinel.new_default
