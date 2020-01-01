"""Request compilation."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Mapping as MappingType, Optional

from preacher.core.request import Request, Parameters
from preacher.core.type import is_scalar
from .error import CompilationError, on_key
from .util import compile_optional_str, for_each, or_default

_KEY_PATH = 'path'
_KEY_HEADERS = 'headers'
_KEY_PARAMS = 'params'


def _validate_param_value_item(item: object):
    if item is None:
        return
    if not is_scalar(item):
        raise CompilationError('Must be a scalar')


def _validate_param_value(value: object):
    if value is None:
        return
    if is_scalar(value):
        return

    if not isinstance(value, list):
        raise CompilationError('Must be a scalar or a list')
    for_each(_validate_param_value_item, value)


def _validate_params(params: object):
    if params is None:
        return
    if isinstance(params, str):
        return
    if not isinstance(params, Mapping):
        raise CompilationError('Must be a string or a mapping')

    for key, value in params.items():
        if not isinstance(key, str):
            raise CompilationError(
                f'A parameter key must be a string, given {key}'
            )
        with on_key(key):
            _validate_param_value(value)


@dataclass(frozen=True)
class _Compiled:
    path: Optional[str] = None
    headers: Optional[MappingType[str, str]] = None
    params: Parameters = None

    def updated(self, updater: _Compiled) -> _Compiled:
        return _Compiled(
            path=or_default(updater.path, self.path),
            headers=or_default(updater.headers, self.headers),
            params=or_default(updater.params, self.params),  # type: ignore
        )

    def to_request(self) -> Request:
        return Request(
            path=or_default(self.path, ''),
            headers=self.headers,
            params=self.params,
        )


def _compile(obj: object) -> _Compiled:
    """`obj` should be a mapping or a string."""

    if isinstance(obj, str):
        return _compile({_KEY_PATH: obj})

    if not isinstance(obj, Mapping):
        raise CompilationError('Must be a mapping or a string')

    path_obj = obj.get(_KEY_PATH)
    with on_key(_KEY_PATH):
        path = compile_optional_str(path_obj)

    headers = obj.get(_KEY_HEADERS)
    if headers is not None and not isinstance(headers, Mapping):
        with on_key(_KEY_HEADERS):
            raise CompilationError(f'Must be a mapping, given {type(path)}')

    params = obj.get(_KEY_PARAMS)
    with on_key(_KEY_PARAMS):
        _validate_params(params)

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
