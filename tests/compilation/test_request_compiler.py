from pytest import raises

from preacher.compilation.error import CompilationError
from preacher.compilation.request import RequestCompiler


def test_given_not_a_string_path():
    compiler = RequestCompiler()

    with raises(CompilationError) as error_info:
        compiler.compile({'path': {'key': 'value'}})
    assert str(error_info.value).endswith(': path')

    with raises(CompilationError) as error_info:
        compiler.of_default({'path': {'key': 'value'}})
    assert str(error_info.value).endswith(': path')


def test_given_not_a_mapping_params():
    compiler = RequestCompiler()

    with raises(CompilationError) as error_info:
        compiler.compile({'params': ''})
    assert str(error_info.value).endswith(': params')

    with raises(CompilationError) as error_info:
        compiler.of_default({'params': ''})
    assert str(error_info.value).endswith(': params')


def test_given_an_empty_mapping():
    compiler = RequestCompiler()
    request = compiler.compile({})
    assert request.path == ''
    assert request.params == {}


def test_given_a_string():
    compiler = RequestCompiler()
    request = compiler.compile('/path')
    assert request.path == '/path'
    assert request.params == {}

    compiler = compiler.of_default('/default-path')
    request = compiler.compile({'params': {'k': 'v'}})
    assert request.path == '/default-path'
    assert request.params == {'k': 'v'}


def test_given_a_filled_mapping():
    compiler = RequestCompiler()
    request = compiler.compile({'path': '/path', 'params': {'key': 'value'}})
    assert request.path == '/path'
    assert request.params == {'key': 'value'}

    compiler = compiler.of_default({
        'path': '/default-path',
        'params': {'k': 'v'},
    })

    request = compiler.compile({})
    assert request.path == '/default-path'
    assert request.params == {'k': 'v'}

    request = compiler.compile('/path')
    assert request.path == '/path'
    assert request.params == {'k': 'v'}

    request = compiler.compile(
        {'path': '/path', 'params': {'key': 'value'}}
    )
    assert request.path == '/path'
    assert request.params == {'key': 'value'}
