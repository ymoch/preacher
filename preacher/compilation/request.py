"""Request compilation."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Mapping as MappingType, Optional

from preacher.core.request import Request
from .error import CompilationError, NamedNode
from .util import or_default


_KEY_PATH = 'path'
_KEY_HEADERS = 'headers'
_KEY_PARAMS = 'params'


@dataclass(frozen=True)
class _Compiled:
    path: Optional[str] = None
    headers: Optional[MappingType[str, str]] = None
    params: Optional[MappingType[str, Any]] = None

    def updated(self, updater: _Compiled) -> _Compiled:
        return _Compiled(
            path=or_default(updater.path, self.path),
            headers=or_default(updater.headers, self.headers),
            params=or_default(updater.params, self.params),
        )

    def to_request(self) -> Request:
        return Request(
            path=or_default(self.path, ''),
            headers=or_default(self.headers, {}),
            params=or_default(self.params, {}),
        )


def _compile(obj) -> _Compiled:
    """`obj` should be a mapping or a string."""

    if isinstance(obj, str):
        return _compile({_KEY_PATH: obj})

    if not isinstance(obj, Mapping):
        raise CompilationError('Must be a mapping or a string')

    path = obj.get(_KEY_PATH)
    if path is not None and not isinstance(path, str):
        raise CompilationError(
            message='Must be a string',
            path=[NamedNode(_KEY_PATH)],
        )

    headers = obj.get(_KEY_HEADERS)
    if headers is not None and not isinstance(headers, Mapping):
        raise CompilationError(
            message='Must be a mapping',
            path=[NamedNode(_KEY_HEADERS)],
        )

    params = obj.get(_KEY_PARAMS)
    if params is not None and not isinstance(params, Mapping):
        raise CompilationError(
            message='Must be a mapping',
            path=[NamedNode(_KEY_PARAMS)],
        )

    return _Compiled(path=path, headers=headers, params=params)


class RequestCompiler:
    def __init__(self, default: _Compiled = None):
        self._default = default or _Compiled()

    def compile(self, obj) -> Request:
        """`obj` should be a mapping or a string."""

        compiled = _compile(obj)
        return self._default.updated(compiled).to_request()

    def of_default(self, obj) -> RequestCompiler:
        """`obj` should be a mapping or a string."""

        compiled = _compile(obj)
        return RequestCompiler(default=compiled)
