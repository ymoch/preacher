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
    ... ) as matcher_mock:
    ...     predicate = compile('string')
    ...     matcher_mock.assert_called_with('string')

    >>> with patch(
    ...     f'{__name__}._compile_single_value_matcher',
    ...     return_value=matcher,
    ... ) as matcher_mock:
    ...     predicate = compile({'key': 'value'})
    ...     matcher_mock.assert_called_with({'key': 'value'})

    """
    if isinstance(obj, str):
        matcher = _compile_static_matcher(obj)
    else:
        matcher = _compile_single_value_matcher(obj)
    return of_hamcrest_matcher(matcher)
