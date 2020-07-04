from typing import Callable, Type, TypeVar

from .error import InterpretationError

T = TypeVar("T")
U = TypeVar("U")


def require_type(tp: Type[T], func: Callable[[T], U]) -> Callable[[object], U]:
    """
    Returns a function
    that asserts its argument should be an instance of `tp`:
    when given an argument that is not an instance of `tp`,
    then throws `InterpretationError`.
    """
    def _func(value: object) -> U:
        if not isinstance(value, tp):
            raise InterpretationError(f"Argument 1 must be a {tp}")
        return func(value)

    return _func
