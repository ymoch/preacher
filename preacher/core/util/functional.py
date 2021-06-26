"""
Functional utilities.
"""

from typing import Any, Callable, TypeVar

T = TypeVar("T")


def identity(value: T, *_args, **_kwargs) -> T:
    """Returns the first argument, ignoring extra arguments."""
    return value


def recursive_map(func: Callable, obj: object) -> object:
    """
    Map `func` recursively, which affects all items in lists
    and all values in dictionaries.
    """
    if isinstance(obj, dict):
        return {k: recursive_map(func, v) for (k, v) in obj.items()}
    if isinstance(obj, list):
        return [recursive_map(func, v) for v in obj]
    return func(obj)


def apply_if_not_none(func: Callable[[object], Any], value: object) -> Any:
    """Apply `func` if `value` is not `None`."""
    if value is None:
        return None
    return func(value)
