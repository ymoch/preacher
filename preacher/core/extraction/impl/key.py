from typing import Optional, Callable, Any

from preacher.core.extraction import Analyzer
from preacher.core.extraction.extraction import Extractor
from preacher.core.util.functional import identity, apply_if_not_none


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
        value = apply_if_not_none(self._cast, analyzer.for_mapping(lambda v: v.get(self._key)))
        return [value] if self._multiple else value
