"""Functional utilities for compilations."""

from collections.abc import Mapping
from functools import partial
from typing import Any, Callable, Iterable, Iterator, TypeVar

from preacher.compilation.error import CompilationError, on_key, on_index

T = TypeVar("T")
U = TypeVar("U")


def map_compile(func: Callable[[T], U], items: Iterable[T]) -> Iterator[U]:
    for idx, item in enumerate(items):
        with on_index(idx):
            yield func(item)


def run_recursively(func: Callable[[object], Any], obj) -> object:
    if isinstance(obj, Mapping):

        def _func(key: object, value: object) -> object:
            if not isinstance(key, str):
                message = f"Key must be a string, given {type(key)}: {key}"
                raise CompilationError(message)
            with on_key(key):
                return run_recursively(func, value)

        return {k: _func(k, v) for (k, v) in obj.items()}

    if isinstance(obj, list):
        _func = partial(run_recursively, func)
        return list(map_compile(_func, obj))
    return func(obj)


def compile_flattening(
    func: Callable[[object], T],
    obj: object,
) -> Iterator[T]:
    """Compile while flattening object, which can be a nested list."""

    if not isinstance(obj, list):
        yield func(obj)
        return

    for idx, item in enumerate(obj):
        with on_index(idx):
            yield from compile_flattening(func, item)
