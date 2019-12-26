"""Predicate compilation."""

from preacher.core.description import Predicate
from preacher.core.predicate import MatcherPredicate
from .matcher import compile as compile_matcher


class PredicateCompiler:

    def compile(self, obj: object) -> Predicate:
        matcher = compile_matcher(obj)
        return MatcherPredicate(matcher)
