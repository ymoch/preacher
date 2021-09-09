"""
Descriptions, which extract a value from an analyzer and test
along the given predicates.
"""

from typing import List, Optional

from preacher.core.context import Context
from preacher.core.extraction import Analyzer, Extractor
from .predicate import Predicate
from .verification import Verification


class Description:
    def __init__(
        self,
        extractor: Extractor,
        predicates: List[Predicate],
        value_name: Optional[str] = None,
    ):
        self._extractor = extractor
        self._predicates = predicates
        self._value_name = value_name

    def verify(self, analyzer: Analyzer, context: Optional[Context] = None) -> Verification:
        try:
            value = self._extractor.extract(analyzer)
        except Exception as error:
            return Verification.of_error(error)

        if self._value_name and context is not None:
            context[self._value_name] = value

        return Verification.collect(
            predicate.verify(value, context) for predicate in self._predicates
        )
