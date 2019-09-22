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
_KEY_MULTIPLE = 'multiple'


class ExtractionCompiler:
    def compile(self, obj: Union[Mapping, str]) -> Extractor:
        if isinstance(obj, str):
            return self.compile({'jq': obj})

        keys = _EXTRACTION_KEYS.intersection(obj.keys())
        if len(keys) != 1:
            raise CompilationError(
                f'Extraction must have only 1 valid key, but has {len(keys)}'
            )
        key = next(iter(keys))

        func = _EXTRACTION_MAP[key]
        query = obj[key]

        multiple = obj.get(_KEY_MULTIPLE, False)
        if not isinstance(multiple, bool):
            raise CompilationError('Must be a boolean', path=[_KEY_MULTIPLE])

        return func(query, multiple=multiple)  # type: ignore
