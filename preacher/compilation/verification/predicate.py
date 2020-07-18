"""Predicate compilation."""

from preacher.core.verification import Predicate, MatcherPredicate
from .matcher import compile_matcher


class PredicateCompiler:

    def compile(self, obj: object) -> Predicate:
        matcher = compile_matcher(obj)
        return MatcherPredicate(matcher)
