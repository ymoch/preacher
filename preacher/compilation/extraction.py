"""Extraction compilation."""
from collections.abc import Mapping
from typing import Any, Callable

from preacher.core.functional import identify
from preacher.core.scenario import (
    Extractor,
    JqExtractor,
    XPathExtractor,
    KeyExtractor,
)
from .error import CompilationError, on_key
from .util import compile_bool, compile_str

_CAST_FUNC_MAP = {
    'int': int,
    'float': float,
    'string': str,
}
_KEY_JQ = 'jq'
_KEY_XPATH = 'xpath'
_KEY_KEY = 'key'
_KEY_MULTIPLE = 'multiple'
_KEY_CAST_TO = 'cast_to'


class ExtractionCompiler:

    def compile(self, obj: object) -> Extractor:
        """`obj` should be a mapping or a string."""

        if isinstance(obj, str):
            return self.compile({_KEY_JQ: obj})

        if not isinstance(obj, Mapping):
            message = f'Must be a map or a string, given {type(obj)}'
            raise CompilationError(message)

        multiple_obj = obj.get(_KEY_MULTIPLE, False)
        with on_key(_KEY_MULTIPLE):
            multiple = compile_bool(multiple_obj)

        cast: Callable[[object], Any] = identify
        cast_obj = obj.get(_KEY_CAST_TO)
        if cast_obj is not None:
            with on_key(_KEY_CAST_TO):
                cast = self._compile_cast(cast_obj)

        if _KEY_JQ in obj:
            query = obj[_KEY_JQ]
            return JqExtractor(query, multiple=multiple, cast=cast)
        if _KEY_XPATH in obj:
            query = obj[_KEY_XPATH]
            return XPathExtractor(query, multiple=multiple, cast=cast)
        if _KEY_KEY in obj:
            key = obj[_KEY_KEY]
            return KeyExtractor(key, cast=cast)
        raise CompilationError('Must have only 1 extraction key, but has 0')

    @staticmethod
    def _compile_cast(obj: object) -> Callable[[object], Any]:
        """`obj` should be a string."""

        key = compile_str(obj)
        cast = _CAST_FUNC_MAP.get(key)
        if not cast:
            raise CompilationError(f'Invalid value: {key}')

        return cast
