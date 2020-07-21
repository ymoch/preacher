"""Predicate compilation."""
from typing import Optional

from preacher.compilation.argument import Arguments, inject_arguments
from preacher.core.verification import Predicate, MatcherPredicate
from .matcher import compile_matcher


class PredicateCompiler:

    def compile(
        self,
        obj: object,
        arguments: Optional[Arguments] = None,
    ) -> Predicate:
        obj = inject_arguments(obj, arguments)
        matcher = compile_matcher(obj)
        return MatcherPredicate(matcher)
