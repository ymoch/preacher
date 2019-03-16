"""Extraction compilation."""

from typing import Callable, Mapping

from preacher.core.extraction import with_jq
from preacher.core.scenario import Extraction
from .error import CompilationError


_EXTRACTION_MAP: Mapping[str, Callable[[str], Extraction]] = {
    'jq': with_jq,
}
_EXTRACTION_KEYS = frozenset(_EXTRACTION_MAP.keys())


def compile(description_object: dict) -> Extraction:
    """
    >>> compile({})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ... has 0

    >>> compile({'jq': '.foo'})({'foo': 'bar'})
    'bar'
    """
    keys = _EXTRACTION_KEYS.intersection(description_object.keys())
    if len(keys) != 1:
        raise CompilationError(
            'Description object must have only 1 valid extraction key'
            f', but has {len(keys)}'
        )
    key = next(iter(keys))

    return _EXTRACTION_MAP[key](description_object[key])
