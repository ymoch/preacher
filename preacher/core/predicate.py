"""
Predicates, which tests a given value.
"""

from abc import ABC, abstractmethod

from .matcher import Matcher, match
from .verification import Verification


class Predicate(ABC):
    """Predicate interface."""

    @abstractmethod
    def verify(self, actual: object, **kwargs) -> Verification:
        raise NotImplementedError()


class MatcherPredicate(Predicate):
    """Predicate of a Hamcrest matcher."""

    def __init__(self, matcher: Matcher):
        self._matcher = matcher

    def verify(self, actual: object, **kwargs) -> Verification:
        return match(self._matcher, actual, **kwargs)
