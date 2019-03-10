"""Predicate."""

import hamcrest
from hamcrest.core.matcher import Matcher as HamcrestMatcher

from .description import Predicate, VerifiedValue
from .verification import Verification


def of_hamcrest_matcher(matcher: HamcrestMatcher) -> Predicate:
    """
    Make a predicate from a Hamcrest matcher.

    >>> from unittest.mock import MagicMock, patch
    >>> matcher = MagicMock(HamcrestMatcher)

    >>> with patch(
    ...     f'{__name__}.hamcrest.assert_that',
    ...     side_effect=AssertionError(' message\\n')
    ... ) as assert_that:
    ...     predicate = of_hamcrest_matcher(matcher)
    ...     verification = predicate(0)
    ...     assert_that.assert_called_with(0, matcher)
    >>> verification.is_valid
    False
    >>> verification.message
    'message'

    >>> with patch(f'{__name__}.hamcrest.assert_that') as assert_that:
    ...     predicate = of_hamcrest_matcher(matcher)
    ...     verification = predicate(1)
    ...     assert_that.assert_called_with(1, matcher)
    >>> verification.is_valid
    True
    """
    def _test(actual: VerifiedValue) -> Verification:
        try:
            hamcrest.assert_that(actual, matcher)
        except AssertionError as error:
            message = str(error).strip()
            return Verification(is_valid=False, message=message)

        return Verification(is_valid=True)

    return _test
