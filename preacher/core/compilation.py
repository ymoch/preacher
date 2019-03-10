"""Compilation."""

from . import predicate
from .description import Predicate


class CompilationError(Exception):
    """Compilation errors."""
    pass


def compile_predicate(value: dict) -> Predicate:
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
    if len(value) != 1:
        raise CompilationError(
            f'Predicate must have only 1 element, but has {len(value)}'
        )
    key, value = next(iter(value.items()))

    if key == 'equal_to':
        return predicate.equal_to(value)

    raise CompilationError(f'Unrecognized predicate key: \'{key}\'')
