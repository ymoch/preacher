"""Utilities for compilations."""

from typing import Callable, Iterable, Iterator, TypeVar

from .error import CompilationError


T = TypeVar('T')
U = TypeVar('U')


def run_on_key(
    key: str,
    func: Callable[[T], U],
    arg: T,
) -> U:
    """
    >>> def succeeding_func(arg):
    ...     return arg
    >>> run_on_key('key', succeeding_func, 1)
    1

    >>> def failing_func(arg):
    ...     raise CompilationError(message='message', path=['path'])
    >>> run_on_key('key', failing_func, 1)
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: message: key.path
    """
    try:
        return func(arg)
    except CompilationError as error:
        raise error.of_parent([key])


def map_on_key(
    key: str,
    func: Callable[[T], U],
    items: Iterable[T],
) -> Iterator[U]:
    """
    >>> def succeeding_func(arg):
    ...     return arg
    >>> results = map_on_key('key', succeeding_func, [1, 2, 3])
    >>> next(results)
    1
    >>> next(results)
    2
    >>> next(results)
    3

    >>> def failing_func(arg):
    ...     if arg == 2:
    ...         raise CompilationError(message='message', path=['path'])
    ...     return arg
    >>> results = map_on_key('key', failing_func, [1, 2, 3])
    >>> next(results)
    1
    >>> next(results)
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: message: key[1].path
    >>> next(results)
    Traceback (most recent call last):
        ...
    StopIteration
    """
    for idx, item in enumerate(items):
        try:
            yield func(item)
        except CompilationError as error:
            raise error.of_parent([f'{key}[{idx}]'])
