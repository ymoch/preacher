from typing import Callable, Iterable, Iterator, TypeVar

from .error import CompilationError


T = TypeVar('T')
U = TypeVar('U')


def run_on_key(
    key: str,
    func: Callable[[T], U],
    arg: T,
) -> U:
    try:
        return func(arg)
    except CompilationError as error:
        raise error.of_parent([key])


def map_on_key(
    key: str,
    func: Callable[[T], U],
    items: Iterable[T],
) -> Iterator[U]:
    for idx, item in enumerate(items):
        try:
            yield func(item)
        except CompilationError as error:
            raise error.of_parent([f'{key}[{idx}]'])
