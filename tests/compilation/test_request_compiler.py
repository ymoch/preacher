from unittest.mock import ANY, patch, sentinel, MagicMock

from pytest import mark, raises, fixture

from preacher.compilation.error import (
    CompilationError,
    NamedNode,
    IndexedNode,
)
from preacher.compilation.request import RequestCompiler, RequestCompiled

PACKAGE = 'preacher.compilation.request'
ctor_patch = patch(f'{PACKAGE}.Request', return_value=sentinel.request)


@fixture
def compiler() -> RequestCompiler:
    return RequestCompiler()


@mark.parametrize('value, expected_path', (
    ([], []),
    ({'path': {'key': 'value'}}, [NamedNode('path')]),
    ({'headers': ''}, [NamedNode('headers')]),
    ({'params': 1}, [NamedNode('params')]),
    ({'params': ['a', 1]}, [NamedNode('params')]),
    ({'params': {1: 2}}, [NamedNode('params')]),
    ({'params': {'k': {'kk': 'vv'}}}, [NamedNode('params'), NamedNode('k')]),
    (
        {'params': {'k': ['a', {}]}},
        [NamedNode('params'), NamedNode('k'), IndexedNode(1)],
    ),
))
def test_given_invalid_values(compiler, value, expected_path):
    with raises(CompilationError) as error_info:
        compiler.compile(value)
    assert error_info.value.path == expected_path


def test_given_an_empty_mapping(compiler):
    compiled = compiler.compile({})
    assert compiled.path is None
    assert compiled.headers is None
    assert compiled.params is None


@mark.parametrize('params', [
    'str',
    {'k1': None, 'k2': 'str', 'k3': [None, 'str']}
])
def test_given_valid_params(compiler, params):
    compiled = compiler.compile({'params': params})
    assert compiled.params == params


def test_given_a_string(compiler):
    compiled = compiler.compile('/path')
    assert compiled.path == 'path'
    assert compiled.headers is None
    assert compiled.params is None


def test_given_a_filled_mapping(compiler):
    compiled = compiler.compile({
        'path': '/path',
        'headers': {'key1': 'value1'},
        'params': {'key': 'value'},
    })
    assert compiled.path == '/path'
    assert compiled.headers == {'key1': 'value1'}
    assert compiled.params == {'key': 'value'}


@patch(f'{PACKAGE}.RequestCompiler', return_value=sentinel.compiler_of_default)
def test_of_default(compiler_ctor, compiler):
    initial_default = MagicMock(RequestCompiled)
    initial_default.replace.return_value = sentinel.new_default

    compiler = RequestCompiler(default=initial_default)
    compiler_of_default = compiler.of_default(sentinel.default)
    assert compiler_of_default is sentinel.compiler_of_default

    initial_default.replace.assert_called_once_with(sentinel.default)

    default = compiler_ctor.call_args[1]['default']
    assert default is sentinel.new_default
