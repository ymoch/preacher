"""Description."""

from typing import Any, Callable, Iterable, Optional

from .verification import Verification


DescribedValue = Optional[dict]
VerifiedValue = Optional[Any]
Extraction = Callable[[DescribedValue], Optional[VerifiedValue]]
Predicate = Callable[[Optional[VerifiedValue]], Verification]


class Description:
    """
    Description.

    >>> from unittest.mock import MagicMock

    When given no predicates, then describes that any described value is valid.
    >>> description = Description(
    ...     extraction=MagicMock(return_value='target'),
    ...     predicates=[],
    ... )
    >>> verification = description.verify('described')
    >>> verification.is_valid
    True
    >>> verification.children
    []
    """

    def __init__(
        self,
        extraction: Extraction,
        predicates: Iterable[Predicate],
    ):
        self._extraction = extraction
        self._predicates = predicates

    def verify(self, value: DescribedValue) -> Verification:
        verified_value = self._extraction(value)
        verifications = [
            predicate(verified_value)
            for predicate in self._predicates
        ]
        is_valid = all(
            verification.is_valid
            for verification in verifications
        )
        return Verification(
            is_valid=is_valid,
            message=None,
            children=verifications
        )
