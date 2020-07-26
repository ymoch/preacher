"""Predicate compilation."""

from typing import Optional

from preacher.compilation.argument import Arguments, inject_arguments
from preacher.core.verification.matcher import MatcherWrappingPredicate
from preacher.core.verification.predicate import Predicate
from .matcher import MatcherFactoryCompiler


class PredicateCompiler:

    def __init__(self, matcher_factory: MatcherFactoryCompiler):
        self._matcher_factory = matcher_factory

    def compile(self, obj: object, arguments: Optional[Arguments] = None) -> Predicate:
        obj = inject_arguments(obj, arguments)
        factory = self._matcher_factory.compile(obj)
        return MatcherWrappingPredicate(factory)
