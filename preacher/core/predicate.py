"""Predicate."""

from typing import Any, Callable

from hamcrest import assert_that
from hamcrest.core.matcher import Matcher

from .status import Status
from .verification import Verification


class MatcherPredicate:
    """Predicate of a Hamcrest matcher."""

    def __init__(self, matcher: Matcher):
        self._matcher = matcher

    def __call__(self, actual: Any, *args: Any, **kwargs: Any) -> Verification:
        try:
            assert_that(actual, self._matcher)
        except AssertionError as error:
            message = str(error).strip()
            return Verification(status=Status.UNSTABLE, message=message)
        except Exception as error:
            return Verification.of_error(error)

        return Verification.succeed()


class DynamicMatcherPredicate:

    def __init__(self, matcher_factory: Callable):
        self._matcher_factory = matcher_factory

    def __call__(self, actual: Any, *args: Any, **kwargs: Any) -> Verification:
        try:
            matcher = self._matcher_factory(*args, **kwargs)
        except Exception as error:
            return Verification.of_error(error)

        predicate = MatcherPredicate(matcher)
        return predicate(actual, *args, **kwargs)
