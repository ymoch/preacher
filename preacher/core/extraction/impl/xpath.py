from typing import Optional, Callable, Any, List

from lxml.etree import _Element as Element, XPathEvalError

from preacher.core.extraction import Analyzer, ExtractionError
from preacher.core.extraction.extraction import Extractor
from preacher.core.util.functional import identity, apply_if_not_none


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

        values = (apply_if_not_none(self._cast, self._convert(element)) for element in elements)
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
            raise ExtractionError(f"Invalid XPath: {self._query}")
