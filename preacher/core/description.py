"""Description."""

from typing import Any, Callable, Iterable

from .verification import Verification


DescribedValue = Any
Extraction = Callable[[DescribedValue], Any]
Predicate = Callable[[Any], Verification]


class Description:
    """
    Description.

    >>> from unittest.mock import MagicMock

    When given no predicates,
    then describes that any described value is valid.
    >>> description = Description(
    ...     extraction=MagicMock(return_value='target'),
    ...     predicates=[],
    ... )
    >>> verification = description.verify('described')
    >>> verification.is_valid
    True
    >>> len(verification.children)
    0

    When given at least one predicates that returns false,
    then describes that it is invalid.
    >>> description = Description(
    ...     extraction=MagicMock(return_value='target'),
    ...     predicates=[
    ...         MagicMock(return_value=Verification(False)),
    ...         MagicMock(return_value=Verification(True)),
    ...     ]
    ... )
    >>> verification = description.verify('described')
    >>> verification.is_valid
    False
    >>> len(verification.children)
    2
    >>> verification.children[0].is_valid
    False
    >>> verification.children[1].is_valid
    True

    When given only predicates that returns true,
    then describes that it is valid.
    >>> description = Description(
    ...     extraction=MagicMock(return_value='target'),
    ...     predicates=[
    ...         MagicMock(return_value=Verification(True)),
    ...         MagicMock(return_value=Verification(True)),
    ...     ]
    ... )
    >>> verification = description.verify('described')
    >>> verification.is_valid
    True
    >>> len(verification.children)
    2
    >>> verification.children[0].is_valid
    True
    >>> verification.children[1].is_valid
    True
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
        return Verification(is_valid=is_valid, children=verifications)
