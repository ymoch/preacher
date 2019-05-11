"""Predicate."""

from __future__ import annotations

from typing import Any

from hamcrest import assert_that
from hamcrest.core.matcher import Matcher

from .status import Status
from .verification import Verification


class MatcherPredicate:
    """
    >>> from unittest.mock import MagicMock, patch
    >>> matcher = MagicMock(Matcher)
    >>> predicate = MatcherPredicate(matcher)

    >>> with patch(
    ...     f'{__name__}.assert_that',
    ...     side_effect=RuntimeError('message')
    ... ) as assert_that:
    ...     verification = predicate(0)
    ...     assert_that.assert_called_with(0, matcher)
    >>> verification.status
    FAILURE
    >>> verification.message
    'RuntimeError: message'

    >>> with patch(
    ...     f'{__name__}.assert_that',
    ...     side_effect=AssertionError(' message\\n')
    ... ) as assert_that:
    ...     verification = predicate(0)
    ...     assert_that.assert_called_with(0, matcher)
    >>> verification.status
    UNSTABLE
    >>> verification.message
    'message'

    >>> with patch(f'{__name__}.assert_that') as assert_that:
    ...     verification = predicate(1)
    ...     assert_that.assert_called_with(1, matcher)
    >>> verification.status
    SUCCESS
    """
    def __init__(self: MatcherPredicate, matcher: Matcher) -> None:
        self._matcher = matcher

    def __call__(self: MatcherPredicate, actual: Any) -> Verification:
        try:
            assert_that(actual, self._matcher)
        except AssertionError as error:
            message = str(error).strip()
            return Verification(status=Status.UNSTABLE, message=message)
        except Exception as error:
            return Verification.of_error(error)

        return Verification.succeed()
