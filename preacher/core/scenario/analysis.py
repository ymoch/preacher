"""
Response body analysis.
"""

import json
from abc import ABC, abstractmethod
from dataclasses import asdict
from datetime import datetime
from typing import Any, Callable, Mapping, TypeVar

from lxml.etree import _Element as Element, XMLParser, fromstring

from preacher.core.response import ResponseBody

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

    @abstractmethod
    def key(self, extract: Callable[[Mapping], T]) -> T:
        raise NotImplementedError()


class JsonAnalyzer(Analyzer):

    def __init__(self, json_body: Any):
        self._json_body = json_body

    def jq(self, extract: Callable[[Any], T]) -> T:
        return extract(self._json_body)

    def xpath(self, extract: Callable[[Element], T]) -> T:
        raise NotImplementedError('XPath extraction is not allowed for JSON')

    def key(self, extract: Callable[[Mapping], T]) -> T:
        if not isinstance(self._json_body, Mapping):
            raise ValueError(
                f'Expected a dictionary, but given {type(self._json_body)}'
            )
        return extract(self._json_body)


class XmlAnalyzer(Analyzer):

    def __init__(self, etree: Element):
        self._etree = etree

    def jq(self, extract: Callable[[Any], T]) -> T:
        raise NotImplementedError('jq extraction is not allowed for XML')

    def xpath(self, extract: Callable[[Element], T]) -> T:
        return extract(self._etree)

    def key(self, extract: Callable[[Mapping], T]) -> T:
        raise NotImplementedError('Key extraction is not allowed for XML')


def analyze_json_str(value: ResponseBody) -> Analyzer:
    return JsonAnalyzer(json.loads(value.text))


def analyze_xml_str(value: ResponseBody) -> Analyzer:
    etree = fromstring(value.content, parser=XMLParser())
    return XmlAnalyzer(etree)


def _to_serializable(value: object) -> object:
    if isinstance(value, dict):
        return {k: _to_serializable(v) for (k, v) in value.items()}
    if isinstance(value, list):
        return [_to_serializable(v) for v in value]
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def analyze_context(context) -> Analyzer:
    return JsonAnalyzer(_to_serializable(asdict(context)))


Analysis = Callable[[ResponseBody], Analyzer]
