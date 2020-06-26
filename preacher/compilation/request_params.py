"""Request parameters compilation."""

from datetime import datetime
from typing import Mapping

from preacher.compilation.error import CompilationError, on_key
from preacher.compilation.util import map_compile
from preacher.core.interpretation.value import RelativeDatetimeValue
from preacher.core.scenario import ParameterValue, Parameter, Parameters


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


def compile_param(value: object) -> Parameter:
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


def compile_params(params: object) -> Parameters:
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
            compiled[key] = compile_param(value)
    return compiled
