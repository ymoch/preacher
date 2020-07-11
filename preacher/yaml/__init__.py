"""
YAML handling.
"""

from typing import TextIO, Iterator

from .error import YamlError
from .loader import Loader, PathLike

__all__ = [
    'YamlError',
    'PathLike',
    'load',
    'load_from_path',
    'load_all',
    'load_all_from_path',
]


def load(stream: TextIO, origin: PathLike = '.') -> object:
    return Loader().load(stream, origin)


def load_from_path(path: PathLike) -> object:
    return Loader().load_from_path(path)


def load_all(stream: TextIO, origin: PathLike = '.') -> Iterator:
    return Loader().load_all(stream, origin)


def load_all_from_path(path: PathLike) -> Iterator:
    return Loader().load_all_from_path(path)
