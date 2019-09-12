"""Description."""

from typing import Any, Callable, List

from .analysis import Analyzer
from .extraction import Extractor
from .status import merge_statuses
from .verification import Verification


Predicate = Callable


class Description:

    def __init__(self, extractor: Extractor, predicates: List[Predicate]):
        self._extractor = extractor
        self._predicates = predicates

    def __call__(self, analyzer: Analyzer, **kwargs: Any) -> Verification:
        """`**kwargs` will be delegated to predicates."""
        try:
            verified_value = self._extractor.extract(analyzer)
        except Exception as error:
            return Verification.of_error(error)

        verifications = [
            predicate(verified_value, **kwargs)
            for predicate in self._predicates
        ]
        status = merge_statuses(v.status for v in verifications)
        return Verification(status, children=verifications)

    @property
    def extractor(self) -> Extractor:
        return self._extractor

    @property
    def predicates(self) -> List[Predicate]:
        return self._predicates
