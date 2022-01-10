"""
Value analysis.
"""

import json
from abc import ABC, abstractmethod
from functools import partial
from typing import Callable, Dict, Generic, Mapping, Optional, TypeVar

from lxml.etree import _Element as Element, XMLParser, fromstring

from preacher.core.request.response import ResponseBody
from preacher.core.util.functional import recursive_map
from preacher.core.util.serialization import to_serializable
from .error import ExtractionError

Source = TypeVar("Source")
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


class _LazyLoader(Generic[Source, T]):
    """Loads an element tree from a binary content lazily."""

    def __init__(
        self,
        source: Source,
        load: Callable[[Source], T],
        error: Optional[ExtractionError] = None,
    ):
        self._source = source
        self._load = load
        self._error: Exception = error or ExtractionError("Load failed once.")

        self._is_loaded = False
        self._target: Optional[T] = None

    def get(self) -> T:
        """
        Load the target value if needed and returns it.

        Returns:
            The loaded element tree.
        Raises:
            ExtractionError: when loading the target has failed once.
        """
        if not self._is_loaded:
            try:
                self._target = self._load(self._source)
            except Exception:
                pass
            self._is_loaded = True

        target = self._target
        if target is None:
            raise self._error
        return target


JSON_LOAD = json.loads
JSON_ERROR = ExtractionError("Not a valid JSON content")
XML_LOAD = partial(fromstring, parser=XMLParser())
XML_ERROR = ExtractionError("Not a valid XML content")


class ResponseBodyAnalyzer(Analyzer):
    def __init__(self, body: ResponseBody):
        self._body = body
        self._etree_loader = _LazyLoader(body.content, XML_LOAD, XML_ERROR)
        self._json_loader = _LazyLoader(body.text, JSON_LOAD, JSON_ERROR)

    def for_text(self, extract: Callable[[str], T]) -> T:
        return extract(self._body.text)

    def for_mapping(self, extract: Callable[[Mapping], T]) -> T:
        json_value = self._json_loader.get()
        if not isinstance(json_value, Mapping):
            raise ExtractionError(f"Expected a dictionary, but given {type(json_value)}")
        return extract(json_value)

    def for_etree(self, extract: Callable[[Element], T]) -> T:
        return extract(self._etree_loader.get())


def _load_mapping(source: Mapping[str, object]) -> Dict[str, object]:
    return {k: v for k, v in source.items()}


class MappingAnalyzer(Analyzer):
    def __init__(self, value: Mapping[str, object]):
        self._loader = _LazyLoader(value, _load_mapping)

    def for_text(self, extract: Callable[[str], T]) -> T:
        # HACK serialize only one time.
        serializable = recursive_map(to_serializable, self._loader.get())
        return extract(json.dumps(serializable, separators=(",", ":")))

    def for_mapping(self, extract: Callable[[Mapping], T]) -> T:
        return extract(self._loader.get())

    def for_etree(self, extract: Callable[[Element], T]) -> T:
        raise ExtractionError("Not an XML content")
