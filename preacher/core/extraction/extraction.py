"""Extraction."""
import json
from abc import ABC, abstractmethod
from functools import partial
from typing import Any, Callable, List, Optional, TypeVar, Iterable

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
            self._cast(value) if value is not None else value
            for value in analyzer.jq(partial(_foo, compiled))
        )
        if self._multiple:
            return list(values)
        else:
            return next(values, None)


def _foo(compiled, text: str) -> Iterable[str]:
    content = compiled.input(text=text).text()
    return (json.loads(line) for line in content.split('\n'))


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
        elements = analyzer.xpath(self._extract)
        if not elements:
            return None

        values = (self._cast(self._convert(element)) for element in elements)
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
        cast: Optional[Callable[[object], Any]] = None,
    ):
        self._key = key
        self._cast = cast or identity

    def extract(self, analyzer: Analyzer) -> object:
        return self._cast(
            analyzer.key(lambda mapping: mapping.get(self._key))
        )
