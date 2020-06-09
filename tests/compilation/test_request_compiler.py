from datetime import date, datetime
from unittest.mock import patch, sentinel, MagicMock

from pytest import mark, raises, fixture

from preacher.compilation.error import (
    CompilationError,
    NamedNode,
    IndexedNode,
)
from preacher.compilation.request import (
    RequestCompiler,
    RequestCompiled,
    compile_param_value,
)

PACKAGE = 'preacher.compilation.request'
DATETIME = datetime.fromisoformat('2020-04-01T01:23:45+09:00')


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
    assert compiled.path == '/path'
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
def test_of_default(compiler_ctor):
    initial_default = MagicMock(RequestCompiled)
    initial_default.replace.return_value = sentinel.new_default

    compiler = RequestCompiler(initial_default)
    compiler_of_default = compiler.of_default(sentinel.default)
    assert compiler_of_default is sentinel.compiler_of_default

    initial_default.replace.assert_called_once_with(sentinel.default)

    default = compiler_ctor.call_args[1]['default']
    assert default is sentinel.new_default


@mark.parametrize('value', [
    complex(1, 2),
    [],
    {},
    frozenset(),
    (date(2019, 12, 31), False),
])
def test_compile_param_value_raises_compilation_error(value):
    with raises(CompilationError):
        compile_param_value(value)


@mark.parametrize('value, expected', [
    (None, None),
    (False, False),
    (0, 0),
    (0.0, 0.0),
    ('', ''),
    (DATETIME, DATETIME),
])
def test_compile_param_value_returns_value(value, expected):
    assert compile_param_value(value) == expected
