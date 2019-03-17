"""Predicate compilation."""

from collections.abc import Mapping
from typing import Union

import hamcrest

from preacher.core.predicate import Predicate, of_hamcrest_matcher
from .error import CompilationError


_STATIC_MATCHER_MAP = {
    # For objects.
    'is_null': hamcrest.is_(hamcrest.none()),
    'is_not_null': hamcrest.is_(hamcrest.not_none()),
    # For collections.
    'is_empty': hamcrest.is_(hamcrest.empty()),
}
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
_PREDICATE_KEYS = frozenset(_VALUE_MATCHER_FUNCTION_MAP.keys())


def compile(obj: Union[str, Mapping]) -> Predicate:
    """
    >>> compile('invalid_key')
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ... 'invalid_key'

    >>> predicate = compile('is_null')
    >>> predicate(None).status.name
    'SUCCESS'
    >>> predicate('SUCCESS').status.name
    'UNSTABLE'

    >>> predicate = compile('is_not_null')
    >>> predicate(None).status.name
    'UNSTABLE'
    >>> predicate('UNSTABLE').status.name
    'SUCCESS'

    >>> predicate = compile('is_empty')
    >>> predicate(None).status.name
    'UNSTABLE'
    >>> predicate(0).status.name
    'UNSTABLE'
    >>> predicate('').status.name
    'SUCCESS'
    >>> predicate([]).status.name
    'SUCCESS'
    >>> predicate('A').status.name
    'UNSTABLE'
    >>> predicate([1]).status.name
    'UNSTABLE'

    >>> compile({})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ... has 0

    >>> compile({'equals_to': 0, 'not': {'equal_to': 1}})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ... has 2

    >>> predicate = compile({'has_length': 1})
    >>> predicate(None).status.name
    'UNSTABLE'
    >>> predicate('').status.name
    'UNSTABLE'
    >>> predicate([]).status.name
    'UNSTABLE'
    >>> predicate('A').status.name
    'SUCCESS'
    >>> predicate([1]).status.name
    'SUCCESS'

    >>> compile({'invalid_key': 0})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ... 'invalid_key'

    >>> predicate = compile({'is': 1})
    >>> predicate(0).status.name
    'UNSTABLE'
    >>> predicate('1').status.name
    'UNSTABLE'
    >>> predicate(1).status.name
    'SUCCESS'

    >>> predicate = compile({'equals_to': 1})
    >>> predicate(0).status.name
    'UNSTABLE'
    >>> predicate('1').status.name
    'UNSTABLE'
    >>> predicate(1).status.name
    'SUCCESS'

    >>> predicate = compile({'is_greater_than': 0})
    >>> predicate(-1).status.name
    'UNSTABLE'
    >>> predicate(0).status.name
    'UNSTABLE'
    >>> predicate(1).status.name
    'SUCCESS'

    >>> predicate = compile({'is_greater_than_or_equal_to': 0})
    >>> predicate(-1).status.name
    'UNSTABLE'
    >>> predicate(0).status.name
    'SUCCESS'
    >>> predicate(1).status.name
    'SUCCESS'

    >>> predicate = compile({'is_less_than': 0})
    >>> predicate(-1).status.name
    'SUCCESS'
    >>> predicate(0).status.name
    'UNSTABLE'
    >>> predicate(1).status.name
    'UNSTABLE'

    >>> predicate = compile({'is_less_than_or_equal_to': 0})
    >>> predicate(-1).status.name
    'SUCCESS'
    >>> predicate(0).status.name
    'SUCCESS'
    >>> predicate(1).status.name
    'UNSTABLE'

    >>> predicate = compile({'contains_string': '0'})
    >>> predicate(0).status.name
    'UNSTABLE'
    >>> predicate('012').status.name
    'SUCCESS'
    >>> predicate('123').status.name
    'UNSTABLE'

    >>> predicate = compile({'starts_with': 'AB'})
    >>> predicate(0).status.name
    'UNSTABLE'
    >>> predicate('ABC').status.name
    'SUCCESS'
    >>> predicate('ACB').status.name
    'UNSTABLE'

    >>> predicate = compile({'ends_with': 'BC'})
    >>> predicate(0).status.name
    'UNSTABLE'
    >>> predicate('ABC').status.name
    'SUCCESS'
    >>> predicate('ACB').status.name
    'UNSTABLE'

    >>> predicate = compile({'matches_regexp': '^A*B$'})
    >>> predicate('B').status.name
    'SUCCESS'
    >>> predicate('ACB').status.name
    'UNSTABLE'

    TODO: Should return `False` when the value type is not `str`.
    >>> predicate(0).status.name
    'FAILURE'
    """
    if isinstance(obj, str):
        matcher = _STATIC_MATCHER_MAP.get(obj)
        if not matcher:
            raise CompilationError(
                f'Invalid predicate: \'{obj}\''
            )
        return of_hamcrest_matcher(matcher)

    if len(obj) != 1:
        raise CompilationError(
            'Predicate must have only 1 element'
            f', but has {len(obj)}'
        )
    key, value = next(iter(obj.items()))
    if key in _VALUE_MATCHER_FUNCTION_MAP:
        matcher = _VALUE_MATCHER_FUNCTION_MAP[key](value)
        return of_hamcrest_matcher(matcher)

    raise CompilationError(f'Unrecognized predicate key: \'{key}\'')
