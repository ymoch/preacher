"""Compilation errors."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class Path:
    node: Optional[str] = None
    index: Optional[int] = None

    def __str__(self) -> str:
        result = ''
        if self.node:
            result += self.node
        if self.index:
            result += f'[{self.index}]'
        return result


class CompilationError(Exception):
    """Compilation errors."""

    def __init__(
        self,
        message: str,
        path: List[str] = [],
        cause: Optional[Exception] = None,
    ):
        super().__init__(message)
        self._message = message
        self._path = [Path(node=p) for p in path]
        self._cause = cause

    @property
    def path(self) -> List[str]:
        return [str(p) for p in self._path]

    def of_parent(self, parent_path: List[str]) -> CompilationError:
        return CompilationError(
            message=self._message,
            path=parent_path + self.path,
            cause=self._cause,
        )

    def __str__(self):
        message = super().__str__()
        if not self._path:
            return message

        path = '.'.join(str(p) for p in self._path)
        return f'{message}: {path}'
