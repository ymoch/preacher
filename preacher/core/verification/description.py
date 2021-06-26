"""
Descriptions, which extract a value from an analyzer and test
along the given predicates.
"""

from typing import List, Optional

from preacher.core.extraction import Analyzer, Extractor
from preacher.core.value import ValueContext
from .predicate import Predicate
from .verification import Verification


class Description:
    def __init__(self, extractor: Extractor, predicates: List[Predicate]):
        self._extractor = extractor
        self._predicates = predicates

    def verify(self, analyzer: Analyzer, context: Optional[ValueContext] = None) -> Verification:
        try:
            verified_value = self._extractor.extract(analyzer)
        except Exception as error:
            return Verification.of_error(error)

        return Verification.collect(
            predicate.verify(verified_value, context) for predicate in self._predicates
        )
