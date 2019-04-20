"""Description."""

from __future__ import annotations

from typing import Any, Callable, List

from .status import merge_statuses
from .verification import Verification

Extraction = Callable[[Any], Any]
Predicate = Callable[[Any], Verification]


class Description:
    """
    Description.

    >>> from .status import Status
    >>> from unittest.mock import MagicMock

    When extraction fails, then description fails.
    >>> description = Description(
    ...     extraction=MagicMock(side_effect=Exception('message')),
    ...     predicates=[]
    ... )
    >>> verification = description('described')
    >>> verification.status
    FAILURE
    >>> verification.message
    'Exception: message'

    When given no predicates,
    then describes that any described value is valid.
    >>> description = Description(
    ...     extraction=MagicMock(return_value='target'),
    ...     predicates=[],
    ... )
    >>> verification = description('described')
    >>> verification.status
    SUCCESS
    >>> len(verification.children)
    0

    When given at least one predicates that returns false,
    then describes that it is invalid.
    >>> description = Description(
    ...     extraction=MagicMock(return_value='target'),
    ...     predicates=[
    ...         MagicMock(return_value=Verification(Status.UNSTABLE)),
    ...         MagicMock(return_value=Verification(Status.FAILURE)),
    ...         MagicMock(return_value=Verification(Status.SUCCESS)),
    ...     ]
    ... )
    >>> verification = description('described')
    >>> verification.status
    FAILURE
    >>> len(verification.children)
    3
    >>> verification.children[0].status
    UNSTABLE
    >>> verification.children[1].status
    FAILURE
    >>> verification.children[2].status
    SUCCESS

    When given only predicates that returns true,
    then describes that it is valid.
    >>> description = Description(
    ...     extraction=MagicMock(return_value='target'),
    ...     predicates=[
    ...         MagicMock(return_value=Verification(Status.SUCCESS)),
    ...         MagicMock(return_value=Verification(Status.SUCCESS)),
    ...     ]
    ... )
    >>> verification = description('described')
    >>> verification.status
    SUCCESS
    >>> len(verification.children)
    2
    >>> verification.children[0].status
    SUCCESS
    >>> verification.children[1].status
    SUCCESS
    """
    def __init__(
        self: Description,
        extraction: Extraction,
        predicates: List[Predicate],
    ):
        self._extraction = extraction
        self._predicates = predicates

    def __call__(self: Description, value: Any) -> Verification:
        try:
            verified_value = self._extraction(value)
        except Exception as error:
            return Verification.of_error(error)

        verifications = [pred(verified_value) for pred in self._predicates]
        status = merge_statuses(v.status for v in verifications)
        return Verification(status, children=verifications)

    @property
    def extraction(self: Description) -> Extraction:
        return self._extraction

    @property
    def predicates(self: Description) -> List[Predicate]:
        return self._predicates
