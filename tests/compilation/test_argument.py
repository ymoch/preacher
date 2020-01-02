from pytest import raises

from preacher.compilation.argument import ArgumentValue, inject_arguments
from preacher.compilation.error import CompilationError


def test_given_single_value():
    value = ArgumentValue('foo')
    assert inject_arguments(value) is None
    assert inject_arguments(value, {'foo': 1}) == 1
    assert inject_arguments(value, {'bar': 2}) is None


def test_given_nested_value():
    value = {
        'foo': ArgumentValue('foo'),
        'bar': [1, ArgumentValue('bar'), 3],
    }
    assert inject_arguments(value, {'foo': 'x', 'bar': 'y'}) == {
        'foo': 'x',
        'bar': [1, 'y', 3],
    }


def test_given_invalid_key():
    value = {1: 2, 3: ArgumentValue('key')}
    with raises(CompilationError):
        inject_arguments(value, {'key': 'value'})
