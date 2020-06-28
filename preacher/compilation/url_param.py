"""URL parameters compilation."""

from datetime import date
from typing import Mapping

from preacher.compilation.error import CompilationError, on_key
from preacher.compilation.util import map_compile
from preacher.core.interpretation.value import RelativeDatetimeValue
from preacher.core.scenario import UrlParams, UrlParam, UrlParamValue


def compile_url_param_value(value: object) -> UrlParamValue:
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
    if isinstance(value, date):
        return value
    if isinstance(value, RelativeDatetimeValue):  # HACK: relax typing.
        return value
    raise CompilationError(
        f'Not allowed type for a request parameter value: {value.__class__}'
    )


def compile_url_param(value: object) -> UrlParam:
    if value is None:
        return value
    if isinstance(value, list):
        return list(map_compile(compile_url_param_value, value))
    try:
        return compile_url_param_value(value)
    except CompilationError as error:
        raise CompilationError(
            f'Not allowed type for a request parameter: {value.__class__}',
            cause=error
        )


def compile_url_params(params: object) -> UrlParams:
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
            compiled[key] = compile_url_param(value)
    return compiled
