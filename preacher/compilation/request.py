"""Request compilation."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Optional

from preacher.core.request import Request, Parameters, ParameterValue
from preacher.core.type import is_scalar, ScalarType
from .error import CompilationError, on_key
from .util import compile_str, compile_mapping, map_compile

_KEY_PATH = 'path'
_KEY_HEADERS = 'headers'
_KEY_PARAMS = 'params'


def _compile_param_value_item(item: object) -> Optional[ScalarType]:
    if item is None:
        return item
    if is_scalar(item):
        return item  # type: ignore
    raise CompilationError('Must be a scalar')


def _compile_param_value(value: object) -> ParameterValue:
    if value is None:
        return value
    if is_scalar(value):
        return value  # type: ignore

    if not isinstance(value, list):
        raise CompilationError('Must be a scalar or a list')
    return list(map_compile(_compile_param_value_item, value))


def _compile_params(params: object) -> Parameters:
    if isinstance(params, str):
        return params

    if not isinstance(params, Mapping):
        raise CompilationError('Must be a string or a mapping')
    compiled = {}
    for key, value in params.items():
        if not isinstance(key, str):
            raise CompilationError(
                f'A parameter key must be a string, given {key}'
            )
        with on_key(key):
            compiled[key] = _compile_param_value(value)
    return compiled


class RequestCompiler:

    def __init__(self, default: Request = None):
        self._default = default or Request()

    def compile(self, obj) -> Request:
        """`obj` should be a mapping or a string."""
        if isinstance(obj, str):
            return self.compile({_KEY_PATH: obj})

        obj = compile_mapping(obj)

        path = self._default.path
        path_obj = obj.get(_KEY_PATH)
        if path_obj is not None:
            with on_key(_KEY_PATH):
                path = compile_str(path_obj)

        headers = self._default.headers
        headers_obj = obj.get(_KEY_HEADERS)
        if headers_obj is not None:
            with on_key(_KEY_HEADERS):
                headers = compile_mapping(headers_obj)

        params = self._default.params
        params_obj = obj.get(_KEY_PARAMS)
        if params_obj is not None:
            with on_key(_KEY_PARAMS):
                _compile_params(params_obj)
                params = params_obj

        return Request(path=path, headers=headers, params=params)

    @staticmethod
    def of_default(default: Request) -> RequestCompiler:
        return RequestCompiler(default=default)
