"""Compilation errors."""

from __future__ import annotations

from dataclasses import dataclass
from functools import reduce
from typing import List, Optional, Union


@dataclass(frozen=True)
class NamedNode:
    name: str

    def __str__(self) -> str:
        return f'.{self.name}'


@dataclass(frozen=True)
class IndexedNode:
    index: int

    def __str__(self) -> str:
        return f'[{self.index}]'


Node = Union[NamedNode, IndexedNode]
Path = List[Node]


class CompilationError(Exception):
    """Compilation errors."""

    def __init__(
        self,
        message: str,
        path: Path = [],
        cause: Optional[Exception] = None,
    ):
        super().__init__(message)
        self._message = message
        self._path = path
        self._cause = cause

    @property
    def path(self) -> Path:
        return self._path

    def of_parent(self, parent_path: Path) -> CompilationError:
        return CompilationError(
            message=self._message,
            path=parent_path + self.path,
            cause=self._cause,
        )

    def __str__(self):
        message = super().__str__()
        if not self._path:
            return message

        path = reduce(lambda lhs, rhs: lhs + str(rhs), self._path, '')
        return f'{message}: {path}'
