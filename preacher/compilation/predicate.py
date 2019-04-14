"""Predicate compilation."""

from typing import Any

from preacher.core.predicate import Predicate, of_hamcrest_matcher
from .matcher import compile as compile_matcher


def compile(obj: Any) -> Predicate:
    """
    >>> from unittest.mock import patch, sentinel

    >>> with patch(
    ...     f'{__name__}.compile_matcher',
    ...     return_value=sentinel.matcher
    ... ) as matcher_mock:
    ...     predicate = compile('matcher')
    ...     matcher_mock.assert_called_with('matcher')
    """
    matcher = compile_matcher(obj)
    return of_hamcrest_matcher(matcher)
