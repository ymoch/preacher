"""
Response body analysis.
"""

import json
from abc import ABC, abstractmethod
from typing import Any, Callable, TypeVar

from lxml.etree import _Element as Element, XMLParser, fromstring

T = TypeVar('T')


class Analyzer(ABC):
    """
    Interface to analyze body.
    """

    @abstractmethod
    def jq(self, extract: Callable[[object], T]) -> T:
        raise NotImplementedError()

    @abstractmethod
    def xpath(self, extract: Callable[[Element], T]) -> T:
        raise NotImplementedError()


class JsonAnalyzer(Analyzer):

    def __init__(self, json_body: Any):
        self._json_body = json_body

    def jq(self, extract: Callable[[Any], T]) -> T:
        return extract(self._json_body)

    def xpath(self, extract: Callable[[Element], T]) -> T:
        raise NotImplementedError('XPath extraction is not allowed for JSON')


class XmlAnalyzer(Analyzer):

    def __init__(self, etree: Element):
        self._etree = etree

    def jq(self, extract: Callable[[Any], T]) -> T:
        raise NotImplementedError('jq extraction is not allowed for XML')

    def xpath(self, extract: Callable[[Element], T]) -> T:
        return extract(self._etree)


def analyze_json_str(value: str) -> Analyzer:
    return JsonAnalyzer(json.loads(value))


def analyze_xml_str(value: str) -> Analyzer:
    etree = fromstring(value, parser=XMLParser())
    return XmlAnalyzer(etree)


Analysis = Callable[[str], Analyzer]
