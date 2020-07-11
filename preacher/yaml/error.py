"""
YAML Error handling.
"""

from contextlib import contextmanager
from typing import Optional, Iterator

from yaml import Mark, Node, MarkedYAMLError

from preacher.compilation import CompilationError


class YamlError:

    def __init__(
        self,
        message: Optional[str] = None,
        mark: Optional[Mark] = None,
        cause: Optional[Exception] = None,
    ):
        self._message = message
        self._mark = mark
        self._cause = cause

    @property
    def message(self) -> Optional[str]:
        if self._message is not None:
            return self._message
        if self._cause:
            return str(self._cause)
        return None

    def __str__(self) -> str:
        lines = []
        message = self.message
        if message is not None:
            lines.append(message)
        if self._mark:
            lines.append(str(self._mark))
        return '\n'.join(lines)


@contextmanager
def on_node(node: Node) -> Iterator:
    try:
        yield
    except CompilationError as error:
        raise YamlError(mark=node.start_mark, cause=error)
    except MarkedYAMLError as error:
        raise YamlError(cause=error)
