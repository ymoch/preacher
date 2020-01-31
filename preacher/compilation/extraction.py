"""Extraction compilation."""
from collections.abc import Mapping
from typing import Any, Callable

from preacher.core.functional import identify
from preacher.core.scenario import Extractor, JqExtractor, XPathExtractor
from .error import CompilationError, on_key
from .util import compile_bool, compile_str

_EXTRACTION_MAP = {
    'jq': JqExtractor,
    'xpath': XPathExtractor,
}
_CAST_FUNC_MAP = {
    'int': int,
    'float': float,
    'string': str,
}
_EXTRACTION_KEYS = frozenset(_EXTRACTION_MAP.keys())
_KEY_MULTIPLE = 'multiple'
_KEY_CAST_TO = 'cast_to'


class ExtractionCompiler:

    def compile(self, obj: object) -> Extractor:
        """`obj` should be a mapping or a string."""

        if isinstance(obj, str):
            return self.compile({'jq': obj})

        if not isinstance(obj, Mapping):
            message = f'Must be a map or a string, given {type(obj)}'
            raise CompilationError(message)

        keys = _EXTRACTION_KEYS.intersection(obj.keys())
        if len(keys) != 1:
            raise CompilationError(
                f'Must have only 1 valid key, but has {len(keys)}'
            )
        key = next(iter(keys))

        func = _EXTRACTION_MAP[key]
        query = obj[key]

        multiple_obj = obj.get(_KEY_MULTIPLE, False)
        with on_key(_KEY_MULTIPLE):
            multiple = compile_bool(multiple_obj)

        cast: Callable[[object], Any] = identify
        cast_obj = obj.get(_KEY_CAST_TO)
        if cast_obj is not None:
            with on_key(_KEY_CAST_TO):
                cast = self._compile_cast(cast_obj)

        return func(query, multiple=multiple, cast=cast)

    @staticmethod
    def _compile_cast(obj: object) -> Callable[[object], Any]:
        """`obj` should be a string."""

        key = compile_str(obj)
        cast = _CAST_FUNC_MAP.get(key)
        if not cast:
            raise CompilationError(f'Invalid value: {key}')

        return cast
