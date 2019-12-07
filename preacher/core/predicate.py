"""Predicate."""

from typing import Any

from .matcher import Matcher, match
from .verification import Verification


class MatcherPredicate:
    """Predicate of a Hamcrest matcher."""

    def __init__(self, matcher: Matcher):
        self._matcher = matcher

    def __call__(self, actual: Any, **kwargs: Any) -> Verification:
        return match(self._matcher, actual, **kwargs)
