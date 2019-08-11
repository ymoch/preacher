"""Request compilation."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Optional, Union

from preacher.core.request import Request
from .error import CompilationError
from .util import or_default


_KEY_PATH = 'path'
_KEY_PARAMS = 'params'


@dataclass(frozen=True)
class _Compiled:
    path: Optional[str] = None
    params: Optional[Mapping] = None

    def to_request(
        self: _Compiled,
        default_path: str,
        default_params: Mapping,
    ) -> Request:
        return Request(
            path=or_default(self.path, default_path),
            params=or_default(self.params, default_params),
        )


def _compile(obj: Union[Mapping, str]) -> _Compiled:
    if isinstance(obj, str):
        return _compile({_KEY_PATH: obj})

    path = obj.get(_KEY_PATH)
    if path is not None and not isinstance(path, str):
        raise CompilationError('Must be a string', path=[_KEY_PATH])

    params = obj.get(_KEY_PARAMS)
    if params is not None and not isinstance(params, Mapping):
        raise CompilationError('Must be a mapping', path=[_KEY_PARAMS])

    return _Compiled(path=path, params=params)


class RequestCompiler:

    def __init__(self, path: str = '', params: Mapping = {}):
        self._path = path
        self._params = params

    def compile(self, obj: Union[Mapping, str]) -> Request:
        compiled = _compile(obj)
        return compiled.to_request(
            default_path=self._path,
            default_params=self._params,
        )

    def of_default(self, obj: Union[Mapping, str]) -> RequestCompiler:
        compiled = _compile(obj)
        return RequestCompiler(
            path=or_default(compiled.path, self._path),
            params=or_default(compiled.params, self._params),
        )
