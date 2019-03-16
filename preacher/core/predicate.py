"""Predicate."""

from typing import Any

from hamcrest import assert_that
from hamcrest.core.matcher import Matcher

from .description import Predicate
from .verification import Status, Verification


def of_hamcrest_matcher(matcher: Matcher) -> Predicate:
    """
    Make a predicate from a Hamcrest matcher.

    >>> from unittest.mock import MagicMock, patch
    >>> matcher = MagicMock(Matcher)

    >>> with patch(
    ...     f'{__name__}.assert_that',
    ...     side_effect=RuntimeError('message')
    ... ) as assert_that:
    ...     predicate = of_hamcrest_matcher(matcher)
    ...     verification = predicate(0)
    ...     assert_that.assert_called_with(0, matcher)
    >>> verification.status.name
    'FAILURE'
    >>> verification.message
    'RuntimeError: message'

    >>> with patch(
    ...     f'{__name__}.assert_that',
    ...     side_effect=AssertionError(' message\\n')
    ... ) as assert_that:
    ...     predicate = of_hamcrest_matcher(matcher)
    ...     verification = predicate(0)
    ...     assert_that.assert_called_with(0, matcher)
    >>> verification.status.name
    'UNSTABLE'
    >>> verification.message
    'message'

    >>> with patch(f'{__name__}.assert_that') as assert_that:
    ...     predicate = of_hamcrest_matcher(matcher)
    ...     verification = predicate(1)
    ...     assert_that.assert_called_with(1, matcher)
    >>> verification.status.name
    'SUCCESS'
    """
    def _test(actual: Any) -> Verification:
        try:
            assert_that(actual, matcher)
        except AssertionError as error:
            message = str(error).strip()
            return Verification(status=Status.UNSTABLE, message=message)
        except Exception as error:
            return Verification.of_error(error)

        return Verification.succeed()

    return _test
