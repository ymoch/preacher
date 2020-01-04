from unittest.mock import ANY, MagicMock, patch, sentinel

from pytest import mark, raises, fixture

from preacher.compilation.error import (
    CompilationError,
    NamedNode,
    IndexedNode,
)
from preacher.compilation.request import RequestCompiler
from preacher.core.request import Request


PACKAGE = 'preacher.compilation.request'
ctor_patch = patch(f'{PACKAGE}.Request', return_value=sentinel.request)


@fixture
def compiler():
    default = MagicMock(Request)
    default.path = sentinel.default_path
    default.headers = sentinel.default_headers
    default.params = sentinel.default_params

    return RequestCompiler(default=default)


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


@ctor_patch
def test_given_an_empty_mapping(ctor, compiler):
    request = compiler.compile({})
    assert request is sentinel.request

    ctor.assert_called_once_with(
        path=sentinel.default_path,
        headers=sentinel.default_headers,
        params=sentinel.default_params,
    )


@mark.parametrize('params', [
    'str',
    {'k1': None, 'k2': 'str', 'k3': [None, 'str']}
])
@ctor_patch
def test_given_valid_params(ctor, compiler, params):
    request = compiler.compile({'params': params})
    assert request is sentinel.request

    ctor.assert_called_once_with(path=ANY, headers=ANY, params=params)


@ctor_patch
def test_given_a_string(ctor, compiler):
    request = compiler.compile('/path')
    assert request is sentinel.request

    ctor.assert_called_once_with(
        path='/path',
        headers=sentinel.default_headers,
        params=sentinel.default_params
    )


@ctor_patch
def test_given_a_filled_mapping(ctor, compiler):
    request = compiler.compile({
        'path': '/path',
        'headers': {'key1': 'value1'},
        'params': {'key': 'value'},
    })
    assert request is sentinel.request

    ctor.assert_called_once_with(
        path='/path',
        headers={'key1': 'value1'},
        params={'key': 'value'},
    )


@patch(f'{PACKAGE}.RequestCompiler', return_value=sentinel.compiler_of_default)
def test_of_default(compiler_ctor, compiler):
    actual = compiler.of_default(sentinel.default)
    assert actual is sentinel.compiler_of_default

    compiler_ctor.assert_called_once_with(default=sentinel.default)
