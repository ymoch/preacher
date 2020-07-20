"""
Descriptions, which extract a value from an analyzer and test
along the given predicates.
"""

from typing import List, Optional

from preacher.core.extraction.analysis import Analyzer
from preacher.core.extraction.extraction import Extractor
from preacher.core.value import ValueContext
from .predicate import Predicate
from .verification import Verification, collect_verification


class Description:

    def __init__(self, extractor: Extractor, predicates: List[Predicate]):
        self._extractor = extractor
        self._predicates = predicates

    def verify(
        self,
        analyzer: Analyzer,
        context: Optional[ValueContext] = None,
    ) -> Verification:
        try:
            verified_value = self._extractor.extract(analyzer)
        except Exception as error:
            return Verification.of_error(error)

        return collect_verification(
            predicate.verify(verified_value, context)
            for predicate in self._predicates
        )

    @property
    def extractor(self) -> Extractor:
        return self._extractor

    @property
    def predicates(self) -> List[Predicate]:
        return self._predicates
