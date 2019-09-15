"""Extraction compilation."""

from collections.abc import Mapping
from typing import Union

from preacher.core.extraction import Extractor, JqExtractor, XPathExtractor
from .error import CompilationError


_EXTRACTION_MAP = {
    'jq': JqExtractor,
    'xpath': XPathExtractor,
}
_EXTRACTION_KEYS = frozenset(_EXTRACTION_MAP.keys())


class ExtractionCompiler:
    def compile(self, obj: Union[Mapping, str]) -> Extractor:
        if isinstance(obj, str):
            return compile({'jq': obj})

        keys = _EXTRACTION_KEYS.intersection(obj.keys())
        if len(keys) != 1:
            raise CompilationError(
                f'Extraction must have only 1 valid key, but has {len(keys)}'
            )
        key = next(iter(keys))

        return _EXTRACTION_MAP[key](obj[key])  # type: ignore


def compile(obj: Union[Mapping, str]) -> Extractor:
    compiler = ExtractionCompiler()
    return compiler.compile(obj)
