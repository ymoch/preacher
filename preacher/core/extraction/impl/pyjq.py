from typing import Optional, Callable, Any

from preacher.core.extraction import Extractor, Analyzer, ExtractionError
from preacher.core.util.functional import identity, apply_if_not_none


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
            import jq
        except ImportError:
            # TODO implement here
            return None

        try:
            compiled = jq.compile(self._query)
        except ValueError:
            raise ExtractionError(f'Invalid jq script: {self._query}')

        values = (
            apply_if_not_none(self._cast, value)
            for value in analyzer.for_text(lambda text: compiled.input(text=text))
        )
        if self._multiple:
            return list(values)
        else:
            return next(values, None)
