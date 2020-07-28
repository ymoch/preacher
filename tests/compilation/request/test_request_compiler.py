from unittest.mock import NonCallableMock, sentinel

from pytest import mark, raises, fixture

from preacher.compilation.argument import Argument
from preacher.compilation.error import CompilationError, NamedNode, IndexedNode
from preacher.compilation.request.request import RequestCompiler, RequestCompiled
from preacher.compilation.request.request_body import RequestBodyCompiler
from preacher.core.request import Method

PKG = 'preacher.compilation.request.request'


@fixture
def body():
    body = NonCallableMock(RequestBodyCompiler)
    body.of_default.return_value = sentinel.new_body_compiler
    return body


@fixture
def default() -> RequestCompiled:
    return RequestCompiled(
        method=sentinel.default_method,
        path=sentinel.default_path,
        headers=sentinel.default_headers,
        params=sentinel.default_params,
        body=sentinel.default_body,
    )


@fixture
def compiler(body, default: RequestCompiled) -> RequestCompiler:
    return RequestCompiler(body=body, default=default)


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


def test_given_an_empty_mapping(compiler: RequestCompiler):
    compiled = compiler.compile({})
    assert compiled.method is sentinel.default_method
    assert compiled.path is sentinel.default_path
    assert compiled.headers is sentinel.default_headers
    assert compiled.params is sentinel.default_params
    assert compiled.body is sentinel.default_body


@mark.parametrize(('method_obj', 'expected'), [
    ('get', Method.GET),
    ('POST', Method.POST),
    ('Put', Method.PUT),
    ('Delete', Method.DELETE),
])
def test_given_a_valid_method(compiler: RequestCompiler, method_obj, expected):
    obj = {'method': Argument('method')}
    arguments = {'method': method_obj}
    compiled = compiler.compile(obj, arguments)
    assert compiled.method is expected


@mark.parametrize('headers_obj', [
    {},
    {'name1': 'value1', 'name2': 'value2'},
])
def test_given_valid_headers(compiler: RequestCompiler, headers_obj):
    obj = {'headers': Argument('headers')}
    arguments = {'headers': headers_obj}
    compiled = compiler.compile(obj, arguments)
    assert compiled.headers == headers_obj


def test_given_an_invalid_params(compiler: RequestCompiler, mocker):
    compile_params = mocker.patch(f'{PKG}.compile_url_params')
    compile_params.side_effect = CompilationError('msg', node=NamedNode('x'))

    with raises(CompilationError) as error_info:
        compiler.compile({'params': sentinel.params})
    assert error_info.value.path == [NamedNode('params'), NamedNode('x')]

    compile_params.assert_called_once_with(sentinel.params, None)


def test_given_valid_params(compiler: RequestCompiler, mocker):
    compile_params = mocker.patch(f'{PKG}.compile_url_params')
    compile_params.return_value = sentinel.compiled_params

    compiled = compiler.compile({'params': sentinel.params}, sentinel.args)
    assert compiled.params == sentinel.compiled_params

    compile_params.assert_called_once_with(sentinel.params, sentinel.args)


def test_given_invalid_body(compiler: RequestCompiler, body):
    body.compile.side_effect = CompilationError('x', node=IndexedNode(1))

    with raises(CompilationError) as error_info:
        compiler.compile({'body': sentinel.body_obj})
    assert error_info.value.path == [NamedNode('body'), IndexedNode(1)]

    body.compile.assert_called_once_with(sentinel.body_obj, None)


def test_given_valid_body(compiler: RequestCompiler, body):
    body.compile.return_value = sentinel.body

    compiled = compiler.compile({'body': sentinel.body_obj}, sentinel.args)
    assert compiled.body is sentinel.body

    body.compile.assert_called_once_with(sentinel.body_obj, sentinel.args)


def test_given_a_string(compiler: RequestCompiler):
    compiled = compiler.compile(Argument('path'), {'path': '/path'})
    assert compiled.method is sentinel.default_method
    assert compiled.path == '/path'
    assert compiled.headers is sentinel.default_headers
    assert compiled.params is sentinel.default_params
    assert compiled.body is sentinel.default_body


def test_of_default_no_body(compiler: RequestCompiler, body, mocker):
    ctor = mocker.patch(f'{PKG}.RequestCompiler')
    ctor.return_value = sentinel.compiler_of_default

    new_default = RequestCompiled(
        method=sentinel.new_default_method,
        path=sentinel.new_default_path,
        headers=sentinel.new_default_headers,
        params=sentinel.new_default_params,
    )
    new_compiler = compiler.of_default(new_default)
    assert new_compiler is sentinel.compiler_of_default

    ctor.assert_called_once_with(
        body=body,
        default=RequestCompiled(
            method=sentinel.new_default_method,
            path=sentinel.new_default_path,
            headers=sentinel.new_default_headers,
            params=sentinel.new_default_params,
            body=sentinel.default_body,
        ),
    )
    body.of_default.assert_not_called()


def test_of_default_body(compiler: RequestCompiler, body, mocker):
    ctor = mocker.patch(f'{PKG}.RequestCompiler')
    ctor.return_value = sentinel.compiler_of_default

    new_default = RequestCompiled(body=sentinel.new_default_body)
    new_compiler = compiler.of_default(new_default)
    assert new_compiler is sentinel.compiler_of_default

    ctor.assert_called_once_with(
        body=sentinel.new_body_compiler,
        default=RequestCompiled(
            method=sentinel.default_method,
            path=sentinel.default_path,
            headers=sentinel.default_headers,
            params=sentinel.default_params,
            body=sentinel.new_default_body,
        ),
    )
    body.of_default.assert_called_once_with(sentinel.new_default_body)
