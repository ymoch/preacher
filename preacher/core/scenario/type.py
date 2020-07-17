"""Typing utilities."""

from functools import partial
from typing import Callable, Type, TypeVar

T = TypeVar("T")
U = TypeVar("U")


def require_type(tp: Type[T], func: Callable[[T], U]) -> Callable[[object], U]:
    """
    Returns a function
    that asserts its argument should be an instance of `tp`:
    when given an argument that is not an instance of `tp`,
    then throws `InterpretationError`.
    """
    return partial(_require_type, tp, func)


def _require_type(tp: Type[T], func: Callable[[T], U], value: object) -> U:
    if not isinstance(value, tp):
        raise TypeError(f"Argument 1 must be a {tp}")
    return func(value)
