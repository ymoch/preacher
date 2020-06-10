"""Request compilation."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from datetime import datetime
from typing import Optional

from preacher.core.interpretation.value import RelativeDatetimeValue
from preacher.core.scenario import (
    Request,
    Parameter,
    Parameters,
    ParameterValue,
)
from .error import CompilationError, on_key
from .util import compile_str, compile_mapping, map_compile, or_else

_KEY_PATH = 'path'
_KEY_HEADERS = 'headers'
_KEY_PARAMS = 'params'


@dataclass(frozen=True)
class RequestCompiled:
    path: Optional[str] = None
    headers: Optional[Mapping] = None
    params: Optional[Parameters] = None

    def replace(self, other: RequestCompiled) -> RequestCompiled:
        return RequestCompiled(
            path=or_else(other.path, self.path),
            headers=or_else(other.headers, self.headers),
            params=other.params if other.params is not None else self.params,
        )

    def fix(self) -> Request:
        return Request(
            path=or_else(self.path, ''),
            headers=self.headers,
            params=self.params,
        )


class RequestCompiler:

    def __init__(self, default: RequestCompiled = None):
        self._default = default or RequestCompiled()

    def compile(self, obj) -> RequestCompiled:
        """`obj` should be a mapping or a string."""

        if isinstance(obj, str):
            return self.compile({_KEY_PATH: obj})

        obj = compile_mapping(obj)
        compiled = self._default

        path_obj = obj.get(_KEY_PATH)
        if path_obj is not None:
            with on_key(_KEY_PATH):
                path = compile_str(path_obj)
            compiled = replace(compiled, path=path)

        headers_obj = obj.get(_KEY_HEADERS)
        if headers_obj is not None:
            with on_key(_KEY_HEADERS):
                headers = compile_mapping(headers_obj)
            compiled = replace(compiled, headers=headers)

        params_obj = obj.get(_KEY_PARAMS)
        if params_obj is not None:
            with on_key(_KEY_PARAMS):
                params = _compile_params(params_obj)
            compiled = replace(compiled, params=params)

        return compiled

    def of_default(self, default: RequestCompiled) -> RequestCompiler:
        return RequestCompiler(default=self._default.replace(default))


def compile_param_value(value: object) -> ParameterValue:
    if value is None:
        return value
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return value
    if isinstance(value, str):
        return value
    if isinstance(value, datetime):
        return value
    if isinstance(value, RelativeDatetimeValue):  # HACK: relax typing.
        return value
    raise CompilationError(
        f'Not allowed type for a request parameter value: {value.__class__}'
    )


def _compile_param(value: object) -> Parameter:
    if value is None:
        return value
    if isinstance(value, list):
        return list(map_compile(compile_param_value, value))
    try:
        return compile_param_value(value)
    except CompilationError as error:
        raise CompilationError(
            f'Not allowed type for a request parameter: {value.__class__}',
            cause=error
        )


def _compile_params(params: object) -> Parameters:
    if isinstance(params, str):
        return params

    if not isinstance(params, Mapping):
        raise CompilationError('Must be a string or a map')
    compiled = {}
    for key, value in params.items():
        if not isinstance(key, str):
            raise CompilationError(
                f'A parameter key must be a string, given {key}'
            )
        with on_key(key):
            compiled[key] = _compile_param(value)
    return compiled
