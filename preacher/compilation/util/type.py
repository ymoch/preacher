"""Typing utilities."""

from typing import Mapping, Optional, TypeVar

from preacher.compilation.error import CompilationError

T = TypeVar("T")


def ensure_bool(obj: object) -> bool:
    """
    Ensure a boolean object.

    Args:
        obj: An ensured object, which should be a `bool` value.
    Returns:
        The compiled value.
    Raises:
        CompilationError: when compilation fails.
    """
    if not isinstance(obj, bool):
        raise CompilationError(f"Must be a boolean, given {type(obj)}")
    return obj


def ensure_str(obj: object) -> str:
    """
    Ensure a string object.

    Args:
        obj: An ensured object, which should be a `string` value.
    Returns:
        The compiled value.
    Raises:
        CompilationError: when compilation fails.
    """
    if not isinstance(obj, str):
        raise CompilationError(f"must be a string, given {type(obj)}")
    return obj


def ensure_optional_str(obj: object) -> Optional[str]:
    """
    Compile an optional string object.

    Args:
        obj: An ensured object, which should be a `string` value or `None`.
    Returns:
        The compiled value.
    Raises:
        CompilationError: when compilation fails.
    """
    if obj is None:
        return None
    return ensure_str(obj)


def ensure_list(obj: object) -> list:
    """
    Ensure a list object.
    When given not a list, then this returns ``[it]``.

    Args:
        obj: A ensured object.
    Returns:
        The compilation result.
    """
    if not isinstance(obj, list):
        return [obj]
    return obj


def ensure_mapping(obj: object) -> Mapping:
    """
    Ensure a mapping object.

    Args:
        obj: A compiled object, which should be a mapping.
    Returns:
        The compile result.
    Raises:
        CompilationError: when compilation fails.
    """
    if not isinstance(obj, Mapping):
        raise CompilationError(f"Must be a map, given {type(obj)}")
    return obj


def or_else(optional: Optional[T], default: T) -> T:
    if optional is None:
        return default
    return optional
