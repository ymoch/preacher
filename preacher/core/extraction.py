"""Extraction."""

from typing import Any, Optional, Union

import pyjq as jq
from lxml.html import HtmlElement

from .analysis import Analyzer


class JqExtractor:

    def __init__(self, query: str):
        self._jq = jq.compile(query).first

    def extract(self, analyzer: Analyzer) -> Any:
        return analyzer.jq(self._jq)


class XPathExtractor:

    def __init__(self, query: str):
        self._query = query

    def extract(self, analyzer: Analyzer) -> str:
        elems = analyzer.xpath(self._extract)
        if not elems:
            return None
        elem = elems[0]

        if isinstance(elem, HtmlElement):
            return elem.text
        return str(elem)

    def _extract(self, etree: HtmlElement) -> Optional[HtmlElement]:
        return etree.xpath(self._query)


Extractor = Union[JqExtractor, XPathExtractor]
