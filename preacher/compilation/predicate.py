"""Predicate compilation."""

from collections.abc import Mapping
from datetime import datetime
from typing import Any, Callable

from hamcrest import greater_than, less_than
from hamcrest.core.matcher import Matcher

from preacher.core.description import Predicate
from preacher.core.datetime import now, parse_datetime
from preacher.core.predicate import MatcherPredicate, DynamicMatcherPredicate
from .datetime import compile_timedelta
from .error import CompilationError, NamedNode
from .matcher import compile as compile_matcher
from .util import run_on_key


PREDICATE_MAP = {
    'be_before': lambda value:
        _compile_datetime_predicate('be_before', value, less_than),
    'be_after': lambda value:
        _compile_datetime_predicate('be_after', value, greater_than),
}


class PredicateCompiler:

    def compile(self, obj: Any) -> Predicate:
        if isinstance(obj, Mapping):
            if len(obj) != 1:
                raise CompilationError(
                    f'Must have only 1 element, but has {len(obj)}'
                )

            key, value = next(iter(obj.items()))
            if key in PREDICATE_MAP:
                return PREDICATE_MAP[key](value)

        matcher = compile_matcher(obj)
        return MatcherPredicate(matcher)


def _compile_datetime_predicate(
    key: str,
    obj: Any,
    matcher_func: Callable[[datetime], Matcher],
) -> DynamicMatcherPredicate:
    if not isinstance(obj, str):
        raise CompilationError('Must be a string', path=[NamedNode(key)])

    delta = run_on_key(key, compile_timedelta, obj)

    def _matcher_factory(*args: Any, **kwargs: Any) -> Matcher:
        origin = kwargs.get('request_datetime') or now()
        return matcher_func(origin + delta)

    return DynamicMatcherPredicate(
        matcher_factory=_matcher_factory,
        converter=parse_datetime,
    )
