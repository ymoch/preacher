"""
Predicates, which tests a given value.
"""

from abc import ABC, abstractmethod
from typing import Optional

from preacher.core.value import AnyContext
from .verification import Verification


class Predicate(ABC):
    """Predicate interface."""

    @abstractmethod
    def verify(self, actual: object, context: Optional[AnyContext] = None) -> Verification:
        ...  # pragma: no cover
