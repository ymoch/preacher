"""Predicate."""

from abc import ABC, abstractmethod
from typing import Any, Optional

from .matcher import Matcher, match
from .verification import Verification


class Predicate(ABC):
    """Predicate interface."""

    @abstractmethod
    def verify(self, actual: Optional[Any], **kwargs) -> Verification:
        raise NotImplementedError()


class MatcherPredicate(Predicate):
    """Predicate of a Hamcrest matcher."""

    def __init__(self, matcher: Matcher):
        self._matcher = matcher

    def verify(self, actual: Optional[Any], **kwargs) -> Verification:
        return match(self._matcher, actual, **kwargs)
