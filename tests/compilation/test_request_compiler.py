from unittest.mock import NonCallableMock, sentinel

from pytest import mark, raises, fixture

from preacher.compilation.error import CompilationError, NamedNode
from preacher.compilation.request import RequestCompiler, RequestCompiled
from preacher.core.scenario import Method

PACKAGE = 'preacher.compilation.request'


@fixture
def compiler() -> RequestCompiler:
    return RequestCompiler()


@mark.parametrize(('obj', 'expected_path'), (
    ([], []),
    ({'method': 1}, [NamedNode('method')]),
    ({'method': 'invalid'}, [NamedNode('method')]),
    ({'path': {'key': 'value'}}, [NamedNode('path')]),
    ({'headers': ''}, [NamedNode('headers')]),
))
def test_given_an_invalid_obj(compiler: RequestCompiler, obj, expected_path):
    with raises(CompilationError) as error_info:
        compiler.compile(obj)
    assert error_info.value.path == expected_path


def test_given_an_invalid_params(compiler: RequestCompiler, mocker):
    compile_params = mocker.patch(
        f'{PACKAGE}.compile_params',
        side_effect=CompilationError('message', path=[NamedNode('x')])
    )
    with raises(CompilationError) as error_info:
        compiler.compile({'params': sentinel.params})
    assert error_info.value.path == [NamedNode('params'), NamedNode('x')]

    compile_params.assert_called_once_with(sentinel.params)


def test_given_an_empty_mapping(compiler: RequestCompiler):
    compiled = compiler.compile({})
    assert compiled.method is None
    assert compiled.path is None
    assert compiled.headers is None
    assert compiled.params is None


@mark.parametrize(('method_obj', 'expected'), [
    ('get', Method.GET),
    ('POST', Method.POST),
    ('Put', Method.PUT),
    ('Delete', Method.DELETE),
])
def test_given_a_valid_method(compiler: RequestCompiler, method_obj, expected):
    compiled = compiler.compile({'method': method_obj})
    assert compiled.method is expected


@mark.parametrize('headers_obj', [
    {},
    {'name1': 'value1', 'name2': 'value2'},
])
def test_given_valid_headers(compiler: RequestCompiler, headers_obj):
    compiled = compiler.compile({'headers': headers_obj})
    assert compiled.headers == headers_obj


def test_given_valid_params(compiler: RequestCompiler, mocker):
    compile_params = mocker.patch(
        f'{PACKAGE}.compile_params',
        return_value=sentinel.compiled_params,
    )

    compiled = compiler.compile({'params': sentinel.params})
    assert compiled.params == sentinel.compiled_params

    compile_params.assert_called_once_with(sentinel.params)


def test_given_a_string(compiler: RequestCompiler):
    compiled = compiler.compile('/path')
    assert compiled.method is None
    assert compiled.path == '/path'
    assert compiled.headers is None
    assert compiled.params is None


def test_of_default(mocker):
    compiler_ctor = mocker.patch(f'{PACKAGE}.RequestCompiler')
    compiler_ctor.return_value = sentinel.compiler_of_default

    initial_default = NonCallableMock(RequestCompiled)
    initial_default.replace.return_value = sentinel.new_default

    compiler = RequestCompiler(initial_default)
    compiler_of_default = compiler.of_default(sentinel.default)
    assert compiler_of_default is sentinel.compiler_of_default

    initial_default.replace.assert_called_once_with(sentinel.default)

    default = compiler_ctor.call_args[1]['default']
    assert default is sentinel.new_default
