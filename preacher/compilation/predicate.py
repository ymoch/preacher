"""Predicate compilation."""

from __future__ import annotations
from typing import Any

from preacher.core.predicate import Predicate, of_hamcrest_matcher
from .matcher import compile as compile_matcher


class PredicateCompiler:
    """
    >>> from unittest.mock import patch, sentinel

    >>> compiler = PredicateCompiler()
    >>> with patch(
    ...     f'{__name__}.compile_matcher',
    ...     return_value=sentinel.matcher
    ... ) as matcher_mock:
    ...     predicate = compiler.compile('matcher')
    ...     matcher_mock.assert_called_with('matcher')
    """
    def compile(self: PredicateCompiler, obj: Any) -> Predicate:
        matcher = compile_matcher(obj)
        return of_hamcrest_matcher(matcher)


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
    compiler = PredicateCompiler()
    return compiler.compile(obj)
