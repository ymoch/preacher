"""Compilation errors."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class Node:
    name: Optional[str] = None
    index: Optional[int] = None

    def __str__(self) -> str:
        result = ''
        if self.name:
            result += self.name
        if self.index:
            result += f'[{self.index}]'
        return result


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

        path = '.'.join(str(node) for node in self._path)
        return f'{message}: {path}'
