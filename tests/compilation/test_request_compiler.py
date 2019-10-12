from pytest import mark, raises

from preacher.compilation.error import CompilationError, NamedNode
from preacher.compilation.request import RequestCompiler


@mark.parametrize('value, expected_path', (
    ([], []),
    ({'path': {'key': 'value'}}, [NamedNode('path')]),
    ({'headers': ''}, [NamedNode('headers')]),
    ({'params': ''}, [NamedNode('params')]),
))
def test_given_invalid_values(value, expected_path):
    compiler = RequestCompiler()

    with raises(CompilationError) as error_info:
        compiler.compile(value)
    assert error_info.value.path == expected_path

    with raises(CompilationError) as error_info:
        compiler.of_default(value)
    assert error_info.value.path == expected_path


def test_given_an_empty_mapping():
    compiler = RequestCompiler()
    request = compiler.compile({})
    assert request.path == ''
    assert request.headers == {}
    assert request.params == {}


def test_given_a_string():
    compiler = RequestCompiler()
    request = compiler.compile('/path')
    assert request.path == '/path'
    assert request.headers == {}
    assert request.params == {}

    compiler = compiler.of_default('/default-path')
    request = compiler.compile({
        'headers': {'k1': 'v1'},
        'params': {'k': 'v'},
    })
    assert request.path == '/default-path'
    assert request.headers == {'k1': 'v1'}
    assert request.params == {'k': 'v'}


def test_given_a_filled_mapping():
    compiler = RequestCompiler()
    request = compiler.compile({
        'path': '/path',
        'headers': {'key1': 'value1'},
        'params': {'key': 'value'},
    })
    assert request.path == '/path'
    assert request.headers == {'key1': 'value1'}
    assert request.params == {'key': 'value'}

    compiler = compiler.of_default({
        'path': '/default-path',
        'headers': {'k1': 'v1'},
        'params': {'k': 'v'},
    })

    request = compiler.compile({})
    assert request.path == '/default-path'
    assert request.headers == {'k1': 'v1'}
    assert request.params == {'k': 'v'}

    request = compiler.compile('/path')
    assert request.path == '/path'
    assert request.headers == {'k1': 'v1'}
    assert request.params == {'k': 'v'}

    request = compiler.compile({
        'path': '/path',
        'headers': {'key1': 'value1'},
        'params': {'key': 'value'},
    })
    assert request.path == '/path'
    assert request.headers == {'key1': 'value1'}
    assert request.params == {'key': 'value'}
