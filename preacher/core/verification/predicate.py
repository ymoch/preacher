"""
Predicates, which tests a given value.
"""

from abc import ABC, abstractmethod
from typing import Optional

from preacher.core.value import ValueContext
from .matcher import Matcher
from .verification import Verification


class Predicate(ABC):
    """Predicate interface."""

    @abstractmethod
    def verify(
        self,
        actual: object,
        context: Optional[ValueContext] = None,
    ) -> Verification:
        raise NotImplementedError()


class MatcherPredicate(Predicate):
    """Predicate of a Hamcrest matcher."""

    def __init__(self, matcher: Matcher):
        self._matcher = matcher

    def verify(
        self,
        actual: object,
        context: Optional[ValueContext] = None,
    ) -> Verification:
        return self._matcher.match(actual, context)
