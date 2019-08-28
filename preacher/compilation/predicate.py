"""Predicate compilation."""

from datetime import timedelta
from typing import Any

from hamcrest import greater_than

from preacher.core.description import Predicate
from preacher.core.predicate import MatcherPredicate, DynamicMatcherPredicate
from preacher.core.util import now, parse_datetime
from .error import CompilationError
from .matcher import compile as compile_matcher


class PredicateCompiler:

    def compile(self, obj: Any) -> Predicate:
        matcher = compile_matcher(obj)
        return MatcherPredicate(matcher)


def after(obj: Any) -> Predicate:
    if not isinstance(obj, int):
        raise CompilationError('must be an integer')
    delta_seconds: int = obj

    delta = timedelta(seconds=delta_seconds)

    def _matcher_factory(*args, **kwargs):
        return greater_than(now() + delta)

    converter = parse_datetime
    return DynamicMatcherPredicate(
        matcher_factory=_matcher_factory,
        converter=converter,
    )
