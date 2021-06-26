"""
Value analysis.
"""

import json
from abc import ABC, abstractmethod
from dataclasses import asdict
from typing import Callable, Mapping, Optional, TypeVar

from lxml.etree import _Element as Element, XMLParser, LxmlError, fromstring

from preacher.core.request.response import ResponseBody
from preacher.core.util.functional import recursive_map
from preacher.core.util.serialization import to_serializable
from .error import ExtractionError

T = TypeVar("T")


class Analyzer(ABC):
    """
    Interface to analyze contents.
    """

    @abstractmethod
    def for_text(self, extract: Callable[[str], T]) -> T:
        ...  # pragma: no cover

    @abstractmethod
    def for_mapping(self, extract: Callable[[Mapping], T]) -> T:
        ...  # pragma: no cover

    @abstractmethod
    def for_etree(self, extract: Callable[[Element], T]) -> T:
        ...  # pragma: no cover


class _LazyElementTreeLoader:
    """Loads an element tree from a binary content lazily."""

    def __init__(self, content: bytes):
        self._content = content
        self._is_loaded = False
        self._etree: Optional[Element] = None

    def get(self) -> Element:
        """
        Load an element tree if needed and returns it.

        Returns:
            The loaded element tree.
        Raises:
            ExtractionError: when loading the element tree has failed once.
        """

        if not self._is_loaded:
            try:
                self._etree = fromstring(self._content, parser=XMLParser())
            except LxmlError:
                pass
            self._is_loaded = True

        etree = self._etree
        if etree is None:
            raise ExtractionError("Not an XML content")
        return etree


class _LazyJsonLoader:
    """Loads a JSON value from a text lazily."""

    def __init__(self, text: str):
        self._text = text
        self._is_loaded = False
        self._is_valid_json = False
        self._value: object = None

    def get(self) -> object:
        """
        Load a JSON value if needed and returns it.

        Returns:
            The loaded JSON value.
        Raises:
            ExtractionError: when loading the JSON value has failed once.
        """

        if not self._is_loaded:
            try:
                self._value = json.loads(self._text)
                self._is_valid_json = True
            except json.JSONDecodeError:
                pass
            self._is_loaded = True

        if not self._is_valid_json:
            raise ExtractionError("Not a JSON content")
        return self._value


class ResponseBodyAnalyzer(Analyzer):
    def __init__(self, body: ResponseBody):
        self._body = body
        self._etree_loader = _LazyElementTreeLoader(body.content)
        self._json_loader = _LazyJsonLoader(body.text)

    def for_text(self, extract: Callable[[str], T]) -> T:
        return extract(self._body.text)

    def for_mapping(self, extract: Callable[[Mapping], T]) -> T:
        json_value = self._json_loader.get()
        if not isinstance(json_value, Mapping):
            raise ExtractionError(f"Expected a dictionary, but given {type(json_value)}")
        return extract(json_value)

    def for_etree(self, extract: Callable[[Element], T]) -> T:
        return extract(self._etree_loader.get())


class MappingAnalyzer(Analyzer):
    def __init__(self, value: Mapping):
        self._value = value

    def for_text(self, extract: Callable[[str], T]) -> T:
        serializable = recursive_map(to_serializable, self._value)
        return extract(json.dumps(serializable, separators=(",", ":")))

    def for_mapping(self, extract: Callable[[Mapping], T]) -> T:
        return extract(self._value)

    def for_etree(self, extract: Callable[[Element], T]) -> T:
        raise ExtractionError("Not an XML content")


def analyze_data_obj(obj) -> Analyzer:
    return MappingAnalyzer(asdict(obj))
