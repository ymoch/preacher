"""Matcher compilation."""

from collections.abc import Mapping
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


_VALUE_MATCHER_FUNCTION_MAP = {
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


def _compile_single_value_matcher(obj: Mapping) -> Matcher:
    """
    >>> _compile_single_value_matcher({})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ... has 0

    >>> _compile_single_value_matcher({'equals_to': 0, 'not': {'equal_to': 1}})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ... has 2

    >>> _compile_single_value_matcher({'invalid_key': 0})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ... 'invalid_key'

    >>> matcher = _compile_single_value_matcher({'has_length': 1})
    >>> assert not matcher.matches(None)
    >>> assert not matcher.matches('')
    >>> assert not matcher.matches([])
    >>> assert matcher.matches('A')
    >>> assert matcher.matches([1])

    >>> matcher = _compile_single_value_matcher({'is': 1})
    >>> assert not matcher.matches(0)
    >>> assert not matcher.matches('1')
    >>> assert matcher.matches(1)

    >>> matcher = _compile_single_value_matcher({'equals_to': 1})
    >>> assert not matcher.matches(0)
    >>> assert not matcher.matches('1')
    >>> assert matcher.matches(1)

    >>> matcher = _compile_single_value_matcher({'is_greater_than': 0})
    >>> assert not matcher.matches(-1)
    >>> assert not matcher.matches(0)
    >>> assert matcher.matches(1)

    >>> matcher = _compile_single_value_matcher(
    ...     {'is_greater_than_or_equal_to': 0}
    ... )
    >>> assert not matcher.matches(-1)
    >>> assert matcher.matches(0)
    >>> assert matcher.matches(1)

    >>> matcher = _compile_single_value_matcher({'is_less_than': 0})
    >>> assert matcher.matches(-1)
    >>> assert not matcher.matches(0)
    >>> assert not matcher.matches(1)

    >>> matcher = _compile_single_value_matcher(
    ...     {'is_less_than_or_equal_to': 0}
    ... )
    >>> assert matcher.matches(-1)
    >>> assert matcher.matches(0)
    >>> assert not matcher.matches(1)

    >>> matcher = _compile_single_value_matcher({'contains_string': '0'})
    >>> assert not matcher.matches(0)
    >>> assert not matcher.matches('123')
    >>> assert matcher.matches('21012')

    >>> matcher = _compile_single_value_matcher({'starts_with': 'AB'})
    >>> assert not matcher.matches(0)
    >>> assert matcher.matches('ABC')
    >>> assert not matcher.matches('ACB')

    >>> matcher = _compile_single_value_matcher({'ends_with': 'BC'})
    >>> assert not matcher.matches(0)
    >>> assert matcher.matches('ABC')
    >>> assert not matcher.matches('ACB')

    >>> matcher = _compile_single_value_matcher({'matches_regexp': '^A*B$'})
    >>> assert not matcher.matches('ACB')
    >>> assert matcher.matches('B')

    TODO: Should return `False` when the value type is not `str`.
    >>> matcher.matches(0)
    Traceback (most recent call last):
        ...
    TypeError: ...
    """
    if len(obj) != 1:
        raise CompilationError(
            f'Must have only 1 element, but has {len(obj)}'
        )

    key, value = next(iter(obj.items()))
    if key not in _VALUE_MATCHER_FUNCTION_MAP:
        raise CompilationError(f'Unrecognized matcher key: \'{key}\'')

    return _VALUE_MATCHER_FUNCTION_MAP[key](value)
