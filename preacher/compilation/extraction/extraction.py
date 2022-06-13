"""Extraction compilation."""

from typing import Any, Callable, Mapping, Optional

from preacher.compilation.error import CompilationError, on_key
from preacher.compilation.util.type import ensure_bool, ensure_mapping, ensure_str
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
_KEY_NAMESPACES = "namespaces"


Factory = Callable[[str, Mapping[str, object]], Extractor]


class ExtractionCompiler:
    def __init__(self):
        self._factory_map = {}

    def add_factory(self, key: str, factory: Factory):
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

        return factory(query, obj)


def _select_multiple(options: Mapping) -> bool:
    obj = options.get(_KEY_MULTIPLE, False)
    with on_key(_KEY_MULTIPLE):
        return ensure_bool(obj)


def _select_cast(options: Mapping) -> Optional[Callable[[object], Any]]:
    obj = options.get(_KEY_CAST_TO)
    if obj is None:
        return None

    with on_key(_KEY_CAST_TO):
        key = ensure_str(obj)
        cast = _CAST_FUNC_MAP.get(key)
        if not cast:
            raise CompilationError(f"Invalid value: {key}")

        return cast


def compile_jq(query: str, options: Mapping) -> JqExtractor:
    multiple = _select_multiple(options)
    cast = _select_cast(options)
    return JqExtractor(PyJqEngine(), query, multiple=multiple, cast=cast)


def _ensure_str_on_key(key: str, obj: object) -> str:
    with on_key(key):
        return ensure_str(obj)


def _select_namespaces(options: Mapping) -> Mapping[str, str]:
    obj = options.get(_KEY_NAMESPACES, {})
    with on_key(_KEY_NAMESPACES):
        mapping = ensure_mapping(obj)
        return {ensure_str(key): _ensure_str_on_key(key, value) for key, value in mapping.items()}


def compile_xpath(query: str, options: Mapping) -> XPathExtractor:
    multiple = _select_multiple(options)
    cast = _select_cast(options)
    namespaces = _select_namespaces(options)

    return XPathExtractor(query, multiple=multiple, cast=cast, namespaces=namespaces)


def compile_key(query: str, options: Mapping) -> KeyExtractor:
    multiple = _select_multiple(options)
    cast = _select_cast(options)
    return KeyExtractor(query, multiple=multiple, cast=cast)


def add_default_extractions(compiler: ExtractionCompiler) -> None:
    if PyJqEngine.is_available():
        compiler.add_factory(_KEY_JQ, compile_jq)
    compiler.add_factory(_KEY_XPATH, compile_xpath)
    compiler.add_factory(_KEY_KEY, compile_key)
