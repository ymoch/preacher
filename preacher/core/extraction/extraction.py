"""Extraction."""

from abc import ABC, abstractmethod
from typing import TypeVar

from .analysis import Analyzer

T = TypeVar("T")


class Extractor(ABC):
    @abstractmethod
    def extract(self, analyzer: Analyzer) -> object:
        """
        Raises:
            EvaluationError: when the evaluation of this extractor fails.
        """
