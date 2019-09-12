"""Description."""

from typing import Any, Callable, List

from .analysis import Analyzer
from .extraction import Extraction
from .status import merge_statuses
from .verification import Verification


Predicate = Callable


class Description:

    def __init__(self, extraction: Extraction, predicates: List[Predicate]):
        self._extraction = extraction
        self._predicates = predicates

    def __call__(self, analyzer: Analyzer, **kwargs: Any) -> Verification:
        """`**kwargs` will be delegated to predicates."""
        try:
            verified_value = analyzer.jq(self._extraction)
        except Exception as error:
            return Verification.of_error(error)

        verifications = [
            predicate(verified_value, **kwargs)
            for predicate in self._predicates
        ]
        status = merge_statuses(v.status for v in verifications)
        return Verification(status, children=verifications)

    @property
    def extraction(self) -> Extraction:
        return self._extraction

    @property
    def predicates(self) -> List[Predicate]:
        return self._predicates
