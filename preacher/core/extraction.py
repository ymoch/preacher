"""Extraction."""

from typing import Any, Callable, List, Optional, Union, TypeVar

import pyjq as jq
from lxml.etree import _Element as Element

from .analysis import Analyzer


T = TypeVar('T')
Cast = Callable[[Optional[Any]], Optional[Any]]


def _default_cast(value: T) -> T:
    return value


class JqExtractor:

    def __init__(
        self,
        query: str,
        multiple: bool = False,
        cast: Optional[Cast] = None,
    ):
        self._query = query
        self._multiple = multiple
        self._cast = cast or _default_cast

        compiled = jq.compile(self._query)
        self._jq = compiled.all

    def extract(self, analyzer: Analyzer) -> Optional[Any]:
        values = (
            self._cast(value) if value is not None else value
            for value in analyzer.jq(self._jq)
        )
        if self._multiple:
            return list(values)
        else:
            return next(values, None)


class XPathExtractor:

    def __init__(
        self,
        query: str,
        multiple: bool = False,
        cast: Optional[Cast] = None,
    ):
        self._query = query
        self._multiple = multiple
        self._cast = cast or _default_cast

    def extract(self, analyzer: Analyzer) -> Optional[Any]:
        elems = analyzer.xpath(self._extract)
        if not elems:
            return None

        values = (self._cast(self._convert(elem)) for elem in elems)
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
