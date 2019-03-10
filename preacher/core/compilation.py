"""Compilation."""

from . import extraction
from . import predicate
from .description import Predicate, Extraction


_EXTRACTION_MAP = {
    'jq': extraction.with_jq,
}


class CompilationError(Exception):
    """Compilation errors."""
    pass


def compile_extraction(description_object: dict) -> Extraction:
    """
    >>> compile_extraction({})
    Traceback (most recent call last):
        ...
    preacher.core.compilation.CompilationError: ... has 0

    >>> compile_extraction({'jq': '.foo'})({'foo': 'bar'})
    'bar'
    """
    keys = (
        frozenset(_EXTRACTION_MAP.keys())
        .intersection(description_object.keys())
    )
    if len(keys) != 1:
        raise CompilationError(
            'Description object must have only 1 valid extraction key'
            f', but has {len(keys)}'
        )
    key = next(iter(keys))

    return _EXTRACTION_MAP[key](description_object[key])


def compile_predicate(predicate_object: dict) -> Predicate:
    """
    >>> compile_predicate({})
    Traceback (most recent call last):
        ...
    preacher.core.compilation.CompilationError: ... has 0

    >>> compile_predicate({'equal_to': 0, 'not': {'equal_to': 1}})
    Traceback (most recent call last):
        ...
    preacher.core.compilation.CompilationError: ... has 2

    >>> compile_predicate({'invalid_key': 0})
    Traceback (most recent call last):
        ...
    preacher.core.compilation.CompilationError: ... 'invalid_key'

    >>> predicate = compile_predicate({'equal_to': 1})
    >>> predicate(0).is_valid
    False
    >>> predicate(1).is_valid
    True
    """
    if len(predicate_object) != 1:
        raise CompilationError(
            'Predicate must have only 1 element'
            f', but has {len(predicate_object)}'
        )
    key, value = next(iter(predicate_object.items()))

    if key == 'equal_to':
        return predicate.equal_to(value)

    raise CompilationError(f'Unrecognized predicate key: \'{key}\'')
