"""Matcher compilation."""

from collections.abc import Mapping
from typing import Any, Union

import hamcrest
from hamcrest.core.matcher import Matcher

from preacher.compilation.error import CompilationError


_STATIC_MATCHER_MAP = {
    # For objects.
    'is_null': hamcrest.is_(hamcrest.none()),
    'is_not_null': hamcrest.is_(hamcrest.not_none()),
    # For collections.
    'is_empty': hamcrest.is_(hamcrest.empty()),
}
_MATCHER_FUNCTION_MAP_TAKING_SINGLE_VALUE = {
    # For objects.
    'is': lambda expected: hamcrest.is_(expected),
    'equals_to': lambda expected: hamcrest.is_(hamcrest.equal_to(expected)),
    'has_length': lambda expected: hamcrest.has_length(expected),
    # For numbers.
    'is_greater_than': (
        lambda value: hamcrest.is_(hamcrest.greater_than(value))
    ),
    'is_greater_than_or_equal_to': (
        lambda value: hamcrest.is_(hamcrest.greater_than_or_equal_to(value))
    ),
    'is_less_than': (
        lambda value: hamcrest.is_(hamcrest.less_than(value))
    ),
    'is_less_than_or_equal_to': (
        lambda value: hamcrest.is_(hamcrest.less_than_or_equal_to(value))
    ),
    # For strings.
    'contains_string': lambda value: hamcrest.contains_string(value),
    'starts_with': lambda value: hamcrest.starts_with(value),
    'ends_with': lambda value: hamcrest.ends_with(value),
    'matches_regexp': lambda value: hamcrest.matches_regexp(value),
}
_MATCHER_FUNCTION_MAP_TAKING_SINGLE_MATCHER = {
    'not': lambda matcher: hamcrest.not_(matcher),
}


def _compile_static_matcher(name: str) -> Matcher:
    """
    >>> _compile_static_matcher('invalid_name')
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ... 'invalid_name'

    >>> matcher = _compile_static_matcher('is_null')
    >>> assert matcher.matches(None)
    >>> assert not matcher.matches(False)

    >>> matcher = _compile_static_matcher('is_not_null')
    >>> assert not matcher.matches(None)
    >>> assert matcher.matches('False')

    >>> matcher = _compile_static_matcher('is_empty')
    >>> assert not matcher.matches(None)
    >>> assert not matcher.matches(0)
    >>> assert matcher.matches('')
    >>> assert not matcher.matches('A')
    >>> assert matcher.matches([])
    >>> assert not matcher.matches([1])
    """
    matcher = _STATIC_MATCHER_MAP.get(name)
    if not matcher:
        raise CompilationError(f'Invalid matcher: \'{name}\'')
    return matcher


def _compile_taking_value(key: str, value: Any) -> Matcher:
    """
    >>> _compile_taking_value('invalid_key', 0)
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ... 'invalid_key'

    >>> matcher = _compile_taking_value('has_length', 1)
    >>> assert not matcher.matches(None)
    >>> assert not matcher.matches('')
    >>> assert not matcher.matches([])
    >>> assert matcher.matches('A')
    >>> assert matcher.matches([1])

    >>> matcher = _compile_taking_value('is', 1)
    >>> assert not matcher.matches(0)
    >>> assert not matcher.matches('1')
    >>> assert matcher.matches(1)

    >>> matcher = _compile_taking_value('equals_to', 1)
    >>> assert not matcher.matches(0)
    >>> assert not matcher.matches('1')
    >>> assert matcher.matches(1)

    >>> matcher = _compile_taking_value('is_greater_than', 0)
    >>> assert not matcher.matches(-1)
    >>> assert not matcher.matches(0)
    >>> assert matcher.matches(1)

    >>> matcher = _compile_taking_value('is_greater_than_or_equal_to', 0)
    >>> assert not matcher.matches(-1)
    >>> assert matcher.matches(0)
    >>> assert matcher.matches(1)

    >>> matcher = _compile_taking_value('is_less_than', 0)
    >>> assert matcher.matches(-1)
    >>> assert not matcher.matches(0)
    >>> assert not matcher.matches(1)

    >>> matcher = _compile_taking_value('is_less_than_or_equal_to', 0)
    >>> assert matcher.matches(-1)
    >>> assert matcher.matches(0)
    >>> assert not matcher.matches(1)

    >>> matcher = _compile_taking_value('contains_string', '0')
    >>> assert not matcher.matches(0)
    >>> assert not matcher.matches('123')
    >>> assert matcher.matches('21012')

    >>> matcher = _compile_taking_value('starts_with', 'AB')
    >>> assert not matcher.matches(0)
    >>> assert matcher.matches('ABC')
    >>> assert not matcher.matches('ACB')

    >>> matcher = _compile_taking_value('ends_with', 'BC')
    >>> assert not matcher.matches(0)
    >>> assert matcher.matches('ABC')
    >>> assert not matcher.matches('ACB')

    >>> matcher = _compile_taking_value('matches_regexp', '^A*B$')
    >>> assert not matcher.matches('ACB')
    >>> assert matcher.matches('B')

    TODO: Should return `False` when the value type is not `str`.
    >>> matcher.matches(0)
    Traceback (most recent call last):
        ...
    TypeError: ...
    """
    func = _MATCHER_FUNCTION_MAP_TAKING_SINGLE_VALUE.get(key)
    if not func:
        raise CompilationError(f'Unrecognized matcher key: \'{key}\'')
    return func(value)


def _compile_taking_single_matcher(key: str, value: Any):
    """
    >>> _compile_taking_single_matcher('invalid_key', '')
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ... 'invalid_key'

    >>> matcher = _compile_taking_single_matcher('not', 1)
    >>> assert matcher.matches('A')
    >>> assert matcher.matches(0)
    >>> assert not matcher.matches(1)

    >>> matcher = _compile_taking_single_matcher('not', {'is_greater_than': 0})
    >>> assert matcher.matches(-1)
    >>> assert matcher.matches(0)
    >>> assert not matcher.matches(1)
    """
    func = _MATCHER_FUNCTION_MAP_TAKING_SINGLE_MATCHER.get(key)
    if not func:
        raise CompilationError(f'Unrecognized matcher key: \'{key}\'')

    if isinstance(value, str) or isinstance(value, Mapping):
        inner = compile(value)
    else:
        inner = hamcrest.equal_to(value)

    return func(inner)


def compile(obj: Union[str, Mapping]) -> Matcher:
    """
    >>> from unittest.mock import patch, sentinel

    >>> compile({})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ... has 0

    >>> compile({'key1': 'value1', 'key2': 'value2'})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ... has 2

    >>> compile({'invalid_key': ''})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ... 'invalid_key'

    >>> with patch(
    ...     f'{__name__}._compile_static_matcher',
    ...     return_value=sentinel.static_matcher,
    ... ) as matcher_mock:
    ...     compile('is_null')
    ...     matcher_mock.assert_called_with('is_null')
    sentinel.static_matcher

    >>> with patch(
    ...     f'{__name__}._compile_taking_value',
    ...     return_value=sentinel.value_matcher,
    ... ) as matcher_mock:
    ...     compile({'equals_to': 'value'})
    ...     matcher_mock.assert_called_with('equals_to', 'value')
    sentinel.value_matcher

    >>> with patch(
    ...     f'{__name__}._compile_taking_single_matcher',
    ...     return_value=sentinel.single_matcher_matcher,
    ... ) as matcher_mock:
    ...     compile({'not': 'value'})
    ...     matcher_mock.assert_called_with('not', 'value')
    sentinel.single_matcher_matcher
    """
    if isinstance(obj, str):
        return _compile_static_matcher(obj)

    if len(obj) != 1:
        raise CompilationError(
            f'Must have only 1 element, but has {len(obj)}'
        )

    key, value = next(iter(obj.items()))

    if key in _MATCHER_FUNCTION_MAP_TAKING_SINGLE_VALUE:
        return _compile_taking_value(key, value)

    if key in _MATCHER_FUNCTION_MAP_TAKING_SINGLE_MATCHER:
        return _compile_taking_single_matcher(key, value)

    raise CompilationError(f'Unrecognized matcher key: \'{key}\'')
