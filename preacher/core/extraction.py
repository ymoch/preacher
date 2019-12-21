"""Extraction."""

from abc import ABC, abstractmethod
from typing import Any, Callable, List, Optional, TypeVar

import pyjq as jq
from lxml.etree import _Element as Element

from .analysis import Analyzer

T = TypeVar('T')
Cast = Callable[[object], Any]


def _default_cast(value: T) -> T:
    return value


class Extractor(ABC):

    @abstractmethod
    def extract(self, analyzer: Analyzer) -> object:
        raise NotImplementedError()


class JqExtractor(Extractor):

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

    def extract(self, analyzer: Analyzer) -> object:
        values = (
            self._cast(value) if value is not None else value
            for value in analyzer.jq(self._jq)
        )
        if self._multiple:
            return list(values)
        else:
            return next(values, None)


class XPathExtractor(Extractor):

    def __init__(
        self,
        query: str,
        multiple: bool = False,
        cast: Optional[Cast] = None,
    ):
        self._query = query
        self._multiple = multiple
        self._cast = cast or _default_cast

    def extract(self, analyzer: Analyzer) -> object:
        elements = analyzer.xpath(self._extract)
        if not elements:
            return None

        values = (self._cast(self._convert(element)) for element in elements)
        if self._multiple:
            return list(values)
        else:
            return next(values, None)

    @staticmethod
    def _convert(elem: Element) -> str:
        if isinstance(elem, Element):
            return elem.text
        return str(elem)

    def _extract(self, elem: Element) -> List[Element]:
        return elem.xpath(self._query)
