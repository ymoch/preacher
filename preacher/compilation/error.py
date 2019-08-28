"""Compilation errors."""

from __future__ import annotations

from typing import List, Optional


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
        self._path = path
        self._cause = cause

    @property
    def path(self) -> List[str]:
        return self._path

    def of_parent(self, parent_path: List[str]) -> CompilationError:
        return CompilationError(
            message=self._message,
            path=parent_path + self._path,
            cause=self._cause,
        )

    def __str__(self):
        message = super().__str__()
        if not self._path:
            return message

        path = '.'.join(self._path)
        return f'{message}: {path}'
