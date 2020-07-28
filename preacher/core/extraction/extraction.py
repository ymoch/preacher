"""Extraction."""

from abc import ABC, abstractmethod
from typing import Any, Callable, List, Optional, TypeVar

import jq
from lxml.etree import _Element as Element, XPathEvalError

from preacher.core.util.functional import identity
from .analysis import Analyzer
from .error import ExtractionError

T = TypeVar('T')


class Extractor(ABC):

    @abstractmethod
    def extract(self, analyzer: Analyzer) -> object:
        """
        Raises:
            EvaluationError: when the evaluation of this extractor fails.
        """
        raise NotImplementedError()


class JqExtractor(Extractor):

    def __init__(
        self,
        query: str,
        multiple: bool = False,
        cast: Optional[Callable[[object], Any]] = None,
    ):
        self._query = query
        self._multiple = multiple
        self._cast = cast or identity

    def extract(self, analyzer: Analyzer) -> object:
        try:
            compiled = jq.compile(self._query)
        except ValueError:
            raise ExtractionError(f'Invalid jq script: {self._query}')

        values = (
            _cast_not_none(self._cast, value)
            for value in analyzer.for_text(lambda text: compiled.input(text=text))
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
        cast: Optional[Callable[[object], Any]] = None,
    ):
        self._query = query
        self._multiple = multiple
        self._cast = cast or identity

    def extract(self, analyzer: Analyzer) -> object:
        elements = analyzer.for_etree(self._extract)
        if not elements:
            return None

        values = (_cast_not_none(self._cast, self._convert(element)) for element in elements)
        if self._multiple:
            return list(values)
        else:
            return next(values, None)

    @staticmethod
    def _convert(elem: object) -> str:
        if isinstance(elem, Element):
            return elem.text
        return str(elem)

    def _extract(self, elem: Element) -> List[Element]:
        try:
            return elem.xpath(self._query)
        except XPathEvalError:
            raise ExtractionError(f'Invalid XPath: {self._query}')


class KeyExtractor(Extractor):

    def __init__(
        self,
        key: str,
        multiple: bool = False,
        cast: Optional[Callable[[object], Any]] = None,
    ):
        self._key = key
        self._multiple = multiple
        self._cast = cast or identity

    def extract(self, analyzer: Analyzer) -> object:
        value = _cast_not_none(self._cast, analyzer.for_mapping(lambda v: v.get(self._key)))
        return [value] if self._multiple else value


def _cast_not_none(cast: Callable[[object], Any], value: object) -> Any:
    if value is None:
        return None
    return cast(value)
