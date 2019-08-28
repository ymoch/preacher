"""Predicate compilation."""

from datetime import datetime
from typing import Any, Callable

from hamcrest import greater_than, less_than
from hamcrest.core.matcher import Matcher

from preacher.core.description import Predicate
from preacher.core.predicate import MatcherPredicate, DynamicMatcherPredicate
from preacher.core.util import parse_datetime
from .error import CompilationError
from .matcher import compile as compile_matcher
from .util import compile_datetime


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

    def _matcher_factory(*args: Any, **kwargs: Any) -> Matcher:
        return matcher_func(compile_datetime(obj))

    return DynamicMatcherPredicate(
        matcher_factory=_matcher_factory,
        converter=parse_datetime,
    )
