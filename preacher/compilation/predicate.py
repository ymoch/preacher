"""Predicate compilation."""

from preacher.core.scenario import Predicate, MatcherPredicate
from .matcher import compile as compile_matcher


class PredicateCompiler:

    def compile(self, obj: object) -> Predicate:
        matcher = compile_matcher(obj)
        return MatcherPredicate(matcher)
