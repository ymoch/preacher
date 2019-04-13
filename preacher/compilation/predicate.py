"""Predicate compilation."""

from collections.abc import Mapping
from typing import Union

import hamcrest

from preacher.core.predicate import Predicate, of_hamcrest_matcher
from .matcher import _compile_static_matcher, _compile_single_value_matcher


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
    >>> from hamcrest.core.matcher import Matcher
    >>> from unittest.mock import MagicMock, patch
    >>> matcher = MagicMock(Matcher)
    >>> with patch(
    ...     f'{__name__}._compile_static_matcher',
    ...     return_value=matcher,
    ... ) as static_matcher_mock:
    ...     predicate = compile('string')
    ...     static_matcher_mock.assert_called_with('string')

    TODO: Move to preacher.compilation.matcher._compile_single_value_matcher
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
        matcher = _compile_static_matcher(obj)
    else:
        matcher = _compile_single_value_matcher(obj)
    return of_hamcrest_matcher(matcher)
