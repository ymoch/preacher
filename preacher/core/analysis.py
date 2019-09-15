import json
from typing import Any, Callable, TypeVar, Union

from lxml.etree import _Element as Element, XMLParser, fromstring


T = TypeVar('T')


class JsonAnalyzer:

    def __init__(self, json_body: Any):
        self._json_body = json_body

    def jq(self, extract: Callable[[Any], T]) -> T:
        return extract(self._json_body)

    def xpath(self, extract: Callable[[Element], T]) -> T:
        raise NotImplementedError('XPath extraction is not allowed for JSON')


class XmlAnalyzer:

    def __init__(self, etree: Element):
        self._etree = etree

    def jq(self, extract: Callable[[Any], T]) -> T:
        raise NotImplementedError('jq extraction is not allowed for XML')

    def xpath(self, extract: Callable[[Element], T]) -> T:
        return extract(self._etree)


Analyzer = Union[JsonAnalyzer, XmlAnalyzer]
Analysis = Callable[[str], Analyzer]


def analyze_json_str(value: str) -> Analyzer:
    return JsonAnalyzer(json.loads(value))


def analyze_xml_str(value: str) -> Analyzer:
    etree = fromstring(value, parser=XMLParser())
    return XmlAnalyzer(etree)
