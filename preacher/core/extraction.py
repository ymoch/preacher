"""Extraction."""

from typing import Any, List, Optional, Union

import pyjq as jq
from lxml.etree import _Element as Element

from .analysis import Analyzer


class JqExtractor:

    def __init__(self, query: str, multiple: bool = False):
        self._query = query
        self._multiple = multiple

        compiled = jq.compile(self._query)
        if multiple:
            self._jq = compiled.all
        else:
            self._jq = compiled.first

    @property
    def query(self) -> str:
        return self._query

    @property
    def multiple(self) -> bool:
        return self._multiple

    def extract(self, analyzer: Analyzer) -> Optional[Any]:
        return analyzer.jq(self._jq)


class XPathExtractor:

    def __init__(self, query: str, multiple: bool = False):
        self._query = query
        self._multiple = multiple

    @property
    def query(self) -> str:
        return self._query

    @property
    def multiple(self) -> bool:
        return self._multiple

    def extract(self, analyzer: Analyzer) -> Optional[Any]:
        elems = analyzer.xpath(self._extract)
        if not elems:
            return None

        values = (self._convert(elem) for elem in elems)
        if self._multiple:
            return list(values)
        else:
            return next(values, None)

    def _convert(self, elem: Element) -> str:
        if isinstance(elem, Element):
            return elem.text
        return str(elem)

    def _extract(self, elem: Element) -> List[Any]:
        return elem.xpath(self._query)


Extractor = Union[JqExtractor, XPathExtractor]
