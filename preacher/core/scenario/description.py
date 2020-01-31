"""
Descriptions, which extract a value from an analyzer and test
along the given predicates.
"""

from typing import Any, List

from .analysis import Analyzer
from .extraction import Extractor
from .predicate import Predicate
from .verification import Verification, collect


class AnalysisDescription:

    def __init__(self, extractor: Extractor, predicates: List[Predicate]):
        self._extractor = extractor
        self._predicates = predicates

    def verify(self, analyzer: Analyzer, **kwargs: Any) -> Verification:
        """`**kwargs` will be delegated to predicates."""
        try:
            verified_value = self._extractor.extract(analyzer)
        except Exception as error:
            return Verification.of_error(error)

        return collect(
            predicate.verify(verified_value, **kwargs)
            for predicate in self._predicates
        )

    @property
    def extractor(self) -> Extractor:
        return self._extractor

    @property
    def predicates(self) -> List[Predicate]:
        return self._predicates
