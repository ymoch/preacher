"""Compilation errors."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import List, Optional, Union, Iterator


@dataclass(frozen=True)
class IndexedNode:
    index: int

    def __str__(self) -> str:
        return f"[{self.index}]"


@dataclass(frozen=True)
class NamedNode:
    name: str

    def __str__(self) -> str:
        return f".{self.name}"


Node = Union[NamedNode, IndexedNode]
Path = List[Node]


def render_path(path: Path) -> str:
    return "".join(str(node) for node in path)


class CompilationError(Exception):
    """Compilation errors."""

    def __init__(
        self,
        message: str,
        node: Optional[Node] = None,
        child: Optional[CompilationError] = None,
        cause: Optional[Exception] = None,
    ):
        self._message = message
        self._node = node
        self._child = child
        self._cause = cause

    @property  # HACK should be cached.
    def path(self) -> Path:
        path = self._child.path if self._child else []
        if self._node:
            path = [self._node] + path
        return path

    def render_path(self) -> str:
        return render_path(self.path)

    def on_node(self, node: Node) -> CompilationError:
        return CompilationError(
            message=self._message,
            node=node,
            child=self,
        )

    def __str__(self) -> str:
        lines = [self._message]
        path = self.path
        if path:
            lines.append(f"  in {render_path(path)}")
        return "\n".join(lines)


@contextmanager
def on_key(key: str) -> Iterator:
    try:
        yield
    except CompilationError as error:
        raise error.on_node(NamedNode(key))


@contextmanager
def on_index(index: int) -> Iterator:
    try:
        yield
    except CompilationError as error:
        raise error.on_node(IndexedNode(index))
