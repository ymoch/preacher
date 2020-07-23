"""Predicate compilation."""

from preacher.core.verification.matcher import HamcrestWrappingPredicate
from preacher.core.verification.predicate import Predicate
from .matcher import compile_hamcrest_factory


class PredicateCompiler:

    def compile(self, obj: object) -> Predicate:
        factory = compile_hamcrest_factory(obj)
        return HamcrestWrappingPredicate(factory)
