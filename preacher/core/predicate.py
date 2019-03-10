"""Predicate."""

from typing import Any, Optional

import hamcrest
from hamcrest.core.matcher import Matcher as HamcrestMatcher

from .description import Predicate, VerifiedValue
from .verification import Verification


def hamcrest_predicate(matcher: HamcrestMatcher) -> Predicate:
    """
    Make a predicate from a Hamcrest matcher.
    """
    def _test(actual: VerifiedValue) -> Verification:
        try:
            hamcrest.assert_that(actual, matcher)
        except AssertionError as error:
            message = str(error).strip()
            return Verification(is_valid=False, message=message)

        return Verification(is_valid=True)

    return _test


def equal_to(expected: Optional[Any]) -> Predicate:
    """
    Returns a predicate that the the target is expected.

    >>> predicate = equal_to(None)
    >>> verification = predicate(None)
    >>> verification.is_valid
    True
    >>> verification = predicate(0)
    >>> verification.is_valid
    False
    >>> verification.message
    'Expected: <None>\\n     but: was <0>'

    >>> predicate = equal_to(1)
    >>> verification = predicate(0)
    >>> verification.is_valid
    False
    >>> verification.message
    'Expected: <1>\\n     but: was <0>'
    >>> verification = predicate('1')
    >>> verification.is_valid
    False
    >>> verification.message
    "Expected: <1>\\n     but: was \'1\'"
    >>> verification = predicate(1)
    >>> verification.is_valid
    True
    """
    return hamcrest_predicate(hamcrest.equal_to(expected))
