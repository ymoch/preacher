"""Extraction."""

from typing import Any, Union

import pyjq as jq

from .analysis import Analyzer


class JqExtractor:

    def __init__(self, query: str):
        self._jq = jq.compile(query).first

    def extract(self, analyzer: Analyzer) -> Any:
        return analyzer.jq(self._jq)


Extractor = Union[JqExtractor]
