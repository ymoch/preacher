"""Predicate compilation."""

from preacher.core.verification.matcher import MatcherWrappingPredicate
from preacher.core.verification.predicate import Predicate
from .matcher import compile_matcher_factory


class PredicateCompiler:

    def compile(self, obj: object) -> Predicate:
        factory = compile_matcher_factory(obj)
        return MatcherWrappingPredicate(factory)
