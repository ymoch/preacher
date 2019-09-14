"""Extraction."""

from typing import Any, List, Optional, Union

import pyjq as jq
from lxml.etree import _Element as Element

from .analysis import Analyzer


class JqExtractor:

    def __init__(self, query: str):
        self._jq = jq.compile(query).first

    def extract(self, analyzer: Analyzer) -> Optional[Any]:
        return analyzer.jq(self._jq)


class XPathExtractor:

    def __init__(self, query: str):
        self._query = query

    def extract(self, analyzer: Analyzer) -> Optional[str]:
        elems = analyzer.xpath(self._extract)
        if not elems:
            return None
        elem = elems[0]

        if isinstance(elem, Element):
            return elem.text

        return str(elem)

    def _extract(self, etree: Element) -> List[Any]:
        return etree.xpath(self._query)


Extractor = Union[JqExtractor, XPathExtractor]
