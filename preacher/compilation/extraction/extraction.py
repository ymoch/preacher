"""Extraction compilation."""

from collections.abc import Mapping
from functools import partial
from typing import Any, Callable, Optional

from preacher.compilation.error import CompilationError, on_key
from preacher.compilation.util.type import ensure_bool, ensure_str
from preacher.core.extraction.extraction import Extractor
from preacher.core.extraction.impl.key import KeyExtractor
from preacher.core.extraction.impl.jq_ import JqExtractor
from preacher.core.extraction.impl.jq_engine import PyJqEngine
from preacher.core.extraction.impl.xpath import XPathExtractor

_CAST_FUNC_MAP = {
    "int": int,
    "float": float,
    "string": str,
}
_KEY_JQ = "jq"
_KEY_XPATH = "xpath"
_KEY_KEY = "key"
_KEY_MULTIPLE = "multiple"
_KEY_CAST_TO = "cast_to"


class ExtractionCompiler:
    def __init__(self):
        self._factory_map = {}

    def add_factory(self, key: str, factory):
        self._factory_map[key] = factory

    def compile(self, obj: object) -> Extractor:
        """`obj` should be a mapping or a string."""

        if isinstance(obj, str):
            return self.compile({_KEY_JQ: obj})

        if not isinstance(obj, Mapping):
            message = f"Must be a map or a string, given {type(obj)}"
            raise CompilationError(message)

        key_candidates = self._factory_map.keys() & obj.keys()
        key_count = len(key_candidates)
        if key_count != 1:
            raise CompilationError(f"Must have only 1 extraction key, but has {key_count}")
        factory_key = next(iter(key_candidates))
        factory = self._factory_map[factory_key]
        query = obj[factory_key]

        multiple_obj = obj.get(_KEY_MULTIPLE, False)
        with on_key(_KEY_MULTIPLE):
            multiple = ensure_bool(multiple_obj)

        cast: Optional[Callable[[object], Any]] = None
        cast_obj = obj.get(_KEY_CAST_TO)
        if cast_obj is not None:
            with on_key(_KEY_CAST_TO):
                cast = self._compile_cast(cast_obj)

        return factory(query, multiple=multiple, cast=cast)

    @staticmethod
    def _compile_cast(obj: object) -> Callable[[object], Any]:
        """`obj` should be a string."""

        key = ensure_str(obj)
        cast = _CAST_FUNC_MAP.get(key)
        if not cast:
            raise CompilationError(f"Invalid value: {key}")

        return cast


def add_default_extractions(compiler: ExtractionCompiler) -> None:
    if PyJqEngine.is_available():
        compiler.add_factory(_KEY_JQ, partial(JqExtractor, PyJqEngine()))
    compiler.add_factory(_KEY_XPATH, XPathExtractor)
    compiler.add_factory(_KEY_KEY, KeyExtractor)
