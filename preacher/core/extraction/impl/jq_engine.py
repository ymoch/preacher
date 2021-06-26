from typing import Iterator

from preacher.core.extraction import ExtractionError
from preacher.core.extraction.impl.jq_ import JqEngine


class PyJqEngine(JqEngine):
    def __init__(self):
        import jq

        self._compile = jq.compile

    def iter(self, query: str, text: str) -> Iterator[object]:
        try:
            compiled = self._compile(query)
        except ValueError:
            raise ExtractionError(f"Invalid jq script: {query}")
        return compiled.input(text=text)

    @staticmethod
    def is_available() -> bool:
        try:
            import jq  # noqa: F401

            return True
        except ImportError:  # pragma: no cover
            return False
