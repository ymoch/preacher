"""Predicate."""

from typing import Any

from hamcrest import assert_that
from hamcrest.core.matcher import Matcher

from .status import Status
from .verification import Verification


class MatcherPredicate:
    """Predicate of a Hamcrest matcher."""

    def __init__(self, matcher: Matcher):
        self._matcher = matcher

    def __call__(self, actual: Any, **kwargs: Any) -> Verification:
        try:
            assert_that(actual, self._matcher)
        except AssertionError as error:
            message = str(error).strip()
            return Verification(status=Status.UNSTABLE, message=message)
        except Exception as error:
            return Verification.of_error(error)

        return Verification.succeed()
