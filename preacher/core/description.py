"""Description."""

from functools import reduce
from typing import Any, Callable, List

from .verification import Status, Verification


Extraction = Callable[[Any], Any]
Predicate = Callable[[Any], Verification]


class Description:
    """
    Description.

    >>> from unittest.mock import MagicMock

    When extraction fails, then description fails.
    >>> description = Description(
    ...     extraction=MagicMock(side_effect=Exception('message')),
    ...     predicates=[]
    ... )
    >>> verification = description('described')
    >>> verification.status.name
    'FAILURE'
    >>> verification.message
    'Extraction failed: message'

    When given no predicates,
    then describes that any described value is valid.
    >>> description = Description(
    ...     extraction=MagicMock(return_value='target'),
    ...     predicates=[],
    ... )
    >>> verification = description('described')
    >>> verification.status.name
    'SUCCESS'
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
    >>> verification.status.name
    'FAILURE'
    >>> len(verification.children)
    3
    >>> verification.children[0].status.name
    'UNSTABLE'
    >>> verification.children[1].status.name
    'FAILURE'
    >>> verification.children[2].status.name
    'SUCCESS'

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
    >>> verification.status.name
    'SUCCESS'
    >>> len(verification.children)
    2
    >>> verification.children[0].status.name
    'SUCCESS'
    >>> verification.children[1].status.name
    'SUCCESS'
    """
    def __init__(self, extraction: Extraction, predicates: List[Predicate]):
        self._extraction = extraction
        self._predicates = predicates

    def __call__(self, value: Any) -> Verification:
        try:
            verified_value = self._extraction(value)
        except Exception as error:
            return Verification(
                status=Status.FAILURE,
                message=f'Extraction failed: {str(error)}'
            )

        verifications = [
            predicate(verified_value)
            for predicate in self._predicates
        ]
        status = reduce(
            lambda a, b: a.merge(b.status),
            verifications,
            Status.SUCCESS
        )
        return Verification(status, children=verifications)
