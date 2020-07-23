"""
Predicates, which tests a given value.
"""

from abc import ABC, abstractmethod
from typing import Optional

from preacher.core.value import ValueContext
from .matcher import HamcrestFactory, match
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

    def __init__(self, matcher: HamcrestFactory):
        self._matcher = matcher

    def verify(
        self,
        actual: object,
        context: Optional[ValueContext] = None,
    ) -> Verification:
        return match(self._matcher, actual, context)
