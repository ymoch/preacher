"""Description."""

from typing import Any, Callable, List

from .status import merge_statuses
from .verification import Verification

Extraction = Callable[[Any], Any]
Predicate = Callable[[Any], Verification]


class Description:

    def __init__(self, extraction: Extraction, predicates: List[Predicate]):
        self._extraction = extraction
        self._predicates = predicates

    def __call__(self, value: Any) -> Verification:
        try:
            verified_value = self._extraction(value)
        except Exception as error:
            return Verification.of_error(error)

        verifications = [pred(verified_value) for pred in self._predicates]
        status = merge_statuses(v.status for v in verifications)
        return Verification(status, children=verifications)

    @property
    def extraction(self) -> Extraction:
        return self._extraction

    @property
    def predicates(self) -> List[Predicate]:
        return self._predicates
