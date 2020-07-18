"""
Functional utilities.
"""

from typing import Callable, TypeVar

T = TypeVar('T')


def identify(value: T, *_args, **_kwargs) -> T:
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
