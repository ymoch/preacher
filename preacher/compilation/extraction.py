"""Extraction compilation."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Union

from preacher.core.extraction import Extraction, with_jq
from .error import CompilationError


_EXTRACTION_MAP = {
    'jq': with_jq,
}
_EXTRACTION_KEYS = frozenset(_EXTRACTION_MAP.keys())


class ExtractionCompiler:
    def compile(
        self: ExtractionCompiler,
        obj: Union[Mapping, str],
    ) -> Extraction:
        if isinstance(obj, str):
            return compile({'jq': obj})

        keys = _EXTRACTION_KEYS.intersection(obj.keys())
        if len(keys) != 1:
            raise CompilationError(
                f'Extraction must have only 1 valid key, but has {len(keys)}'
            )
        key = next(iter(keys))

        return _EXTRACTION_MAP[key](obj[key])


def compile(obj: Union[Mapping, str]) -> Extraction:
    """
    >>> compile({})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ... has 0

    >>> compile('.foo')({'foo': 'bar'})
    'bar'

    >>> compile({'jq': '.foo'})({'foo': 'bar'})
    'bar'
    """
    compiler = ExtractionCompiler()
    return compiler.compile(obj)
