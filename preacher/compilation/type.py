"""Typing utilities."""

from typing import Mapping, Optional, TypeVar

from preacher.compilation.error import CompilationError

T = TypeVar('T')


def compile_bool(obj: object) -> bool:
    """
    Compile the given boolean object.

    Args:
        obj: A compiled object, which should be a `bool` value.
    Returns:
        The compiled value.
    Raises:
        CompilationError: when compilation fails.
    """
    if not isinstance(obj, bool):
        raise CompilationError(f'Must be a boolean, given {type(obj)}')
    return obj


def compile_str(obj: object) -> str:
    """
    Compile the given string object.

    Args:
        obj: A compiled object, which should be a `string` value.
    Returns:
        The compiled value.
    Raises:
        CompilationError: when compilation fails.
    """
    if not isinstance(obj, str):
        raise CompilationError(f'must be a string, given {type(obj)}')
    return obj


def compile_optional_str(obj: object) -> Optional[str]:
    """
    Compile the given optional string object.

    Args:
        obj: A compiled object, which should be a `string` value or `None`.
    Returns:
        The compiled value.
    Raises:
        CompilationError: when compilation fails.
    """
    if obj is None:
        return None
    return compile_str(obj)


def compile_list(obj: object) -> list:
    """
    Compile the given list object.
    When given not a list, then this returns ``[it]``.

    Args:
        obj: A compiled object.
    Returns:
        The compilation result.
    """
    if not isinstance(obj, list):
        return [obj]
    return obj


def compile_mapping(obj: object) -> Mapping:
    """
    Compile the given mapping object.

    Args:
        obj: A compiled object, which should be a mapping.
    Returns:
        The compile result.
    Raises:
        CompilationError: when compilation fails.
    """
    if not isinstance(obj, Mapping):
        raise CompilationError(f'Must be a map, given {type(obj)}')
    return obj


def or_else(optional: Optional[T], default: T) -> T:
    if optional is None:
        return default
    return optional
