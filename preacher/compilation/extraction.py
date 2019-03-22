"""Extraction compilation."""

from collections.abc import Mapping

from preacher.core.extraction import Extraction, with_jq
from .error import CompilationError


_EXTRACTION_MAP = {
    'jq': with_jq,
}
_EXTRACTION_KEYS = frozenset(_EXTRACTION_MAP.keys())


def compile(extraction_obj: Mapping) -> Extraction:
    """
    >>> compile({})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ... has 0

    >>> compile({'jq': '.foo'})({'foo': 'bar'})
    'bar'
    """
    keys = _EXTRACTION_KEYS.intersection(extraction_obj.keys())
    if len(keys) != 1:
        raise CompilationError(
            'Description object must have only 1 valid extraction key'
            f', but has {len(keys)}'
        )
    key = next(iter(keys))

    return _EXTRACTION_MAP[key](extraction_obj[key])
