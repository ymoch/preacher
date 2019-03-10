"""Predicate."""

from typing import Any, Optional

from .description import Predicate, VerifiedValue
from .verification import Verification


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
    'Expected: equal to None, Actual: 0'

    >>> predicate = equal_to(1)
    >>> verification = predicate(0)
    >>> verification.is_valid
    False
    >>> verification.message
    'Expected: equal to 1, Actual: 0'
    >>> verification = predicate('1')
    >>> verification.is_valid
    False
    >>> verification.message
    'Expected: equal to 1, Actual: 1'
    >>> verification = predicate(1)
    >>> verification.is_valid
    True
    """
    def test(actual: VerifiedValue) -> Verification:
        is_valid = actual == expected
        return Verification(
            is_valid=is_valid,
            message=f'Expected: equal to {expected}, Actual: {actual}',
        )
    return test
