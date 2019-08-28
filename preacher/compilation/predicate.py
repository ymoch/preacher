"""Predicate compilation."""

from datetime import datetime
from typing import Any, Callable

from hamcrest import greater_than, less_than
from hamcrest.core.matcher import Matcher

from preacher.core.description import Predicate
from preacher.core.predicate import MatcherPredicate, DynamicMatcherPredicate
from preacher.core.util import now, parse_datetime
from .datetime import compile_relative_datetime
from .error import CompilationError
from .matcher import compile as compile_matcher


def before(obj: Any) -> Predicate:
    return _compile_datetime_predicate('before', obj, less_than)


def after(obj: Any) -> Predicate:
    return _compile_datetime_predicate('after', obj, greater_than)


class PredicateCompiler:

    def compile(self, obj: Any) -> Predicate:
        matcher = compile_matcher(obj)
        return MatcherPredicate(matcher)


def _compile_datetime_predicate(
    key: str,
    obj: Any,
    matcher_func: Callable[[datetime], Matcher],
) -> DynamicMatcherPredicate:
    if not isinstance(obj, str):
        raise CompilationError(f'Predicate.{key} must be a string')
    try:
        delta = compile_relative_datetime(obj)
    except CompilationError as error:
        raise CompilationError(
            message=f'Predicate.{key} has a nvalid format value: {obj}',
            cause=error,
        )

    def _matcher_factory(*args: Any, **kwargs: Any) -> Matcher:
        return matcher_func(now() + delta)

    return DynamicMatcherPredicate(
        matcher_factory=_matcher_factory,
        converter=parse_datetime,
    )
