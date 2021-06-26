from abc import ABC, abstractmethod
from functools import partial
from typing import Any, Callable, Iterator, Optional

from preacher.core.extraction import Extractor, Analyzer
from preacher.core.util.functional import identity, apply_if_not_none


class JqEngine(ABC):
    @abstractmethod
    def iter(self, query: str, value: str) -> Iterator[object]:
        ...  # pragma: no cover


class JqExtractor(Extractor):
    def __init__(
        self,
        engine: JqEngine,
        query: str,
        multiple: bool = False,
        cast: Optional[Callable[[object], Any]] = None,
    ):
        self._engine = engine
        self._query = query
        self._multiple = multiple
        self._cast = cast or identity

    def extract(self, analyzer: Analyzer) -> object:
        values = (
            apply_if_not_none(self._cast, value)
            for value in analyzer.for_text(partial(self._engine.iter, self._query))
        )
        if self._multiple:
            return list(values)
        else:
            return next(values, None)
