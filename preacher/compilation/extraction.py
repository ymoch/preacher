"""Extraction compilation."""

from collections.abc import Mapping

from preacher.core.extraction import (
    Cast,
    Extractor,
    JqExtractor,
    XPathExtractor,
)
from .error import CompilationError, NamedNode
from .util import run_on_key


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

    def compile(self, obj) -> Extractor:
        """`obj` should be a mapping or a string."""

        if isinstance(obj, str):
            return self.compile({'jq': obj})

        if not isinstance(obj, Mapping):
            raise CompilationError('Must be a mapping or a string')

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
            raise CompilationError(
                message='Must be a boolean',
                path=[NamedNode(_KEY_MULTIPLE)],
            )

        cast = None
        cast_obj = obj.get(_KEY_CAST_TO)
        if cast_obj is not None:
            cast = run_on_key(_KEY_CAST_TO, self._compile_cast, cast_obj)

        return func(query, multiple=multiple, cast=cast)  # type: ignore

    def _compile_cast(self, obj) -> Cast:
        if not isinstance(obj, str):
            raise CompilationError('Must be a string')

        cast = _CAST_FUNC_MAP.get(obj)  # type: ignore
        if not cast:
            raise CompilationError(f'Invalid value: {obj}')

        return cast
