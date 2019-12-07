"""Predicate."""

from typing import Any, Callable

from .internal.functional import identify
from .matcher import Matcher
from .verification import Verification


class MatcherPredicate:
    """Predicate of a Hamcrest matcher."""

    def __init__(self, matcher: Matcher):
        self._matcher = matcher

    def __call__(self, actual: Any, **kwargs: Any) -> Verification:
        return self._matcher.verify(actual, **kwargs)


class DynamicMatcherPredicate:
    """Predicate of a dynamic Hamcrest matcher and conversion."""

    def __init__(
        self,
        matcher_factory: Callable,
        converter: Callable[[Any], Any] = identify,
    ):
        self._matcher_factory = matcher_factory
        self._converter = converter

    def __call__(self, actual: Any, **kwargs: Any) -> Verification:
        try:
            matcher = self._matcher_factory(**kwargs)
            predicated_value = self._converter(actual)
        except Exception as error:
            return Verification.of_error(error)

        predicate = MatcherPredicate(matcher)
        return predicate(predicated_value, **kwargs)
