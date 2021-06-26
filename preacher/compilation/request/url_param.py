"""URL parameters compilation."""

from datetime import date
from typing import Mapping, Optional

from preacher.compilation.argument import Arguments, inject_arguments
from preacher.compilation.error import CompilationError, on_key
from preacher.compilation.util.functional import map_compile
from preacher.core.request import UrlParams, UrlParam, UrlParamValue
from preacher.core.value.impl.datetime import DatetimeValueWithFormat


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
    if isinstance(value, DatetimeValueWithFormat):  # HACK: relax typing.
        return value
    raise CompilationError(f"Not allowed type for a request parameter value: {value.__class__}")


def compile_url_param(value: object) -> UrlParam:
    if value is None:
        return value
    if isinstance(value, list):
        return list(map_compile(compile_url_param_value, value))
    try:
        return compile_url_param_value(value)
    except CompilationError as error:
        raise CompilationError(
            f"Not allowed type for a request parameter: {value.__class__}", cause=error
        )


def compile_url_params(
    obj: object,
    arguments: Optional[Arguments] = None,
) -> UrlParams:
    """
    Compiles an object into URL parameters.

    Args:
        obj: A compiled object, which should be a mapping or a string.
        arguments: Arguments to inject.
    Returns:
        The result of compilation.
    Raises:
        CompilationError: when compilation fails.
    """
    obj = inject_arguments(obj, arguments)

    if isinstance(obj, str):
        return obj

    if not isinstance(obj, Mapping):
        raise CompilationError("Must be a mapping or a string")

    compiled = {}
    for key, value in obj.items():
        assert isinstance(key, str)  # Satisfied in injecting arguments.
        with on_key(key):
            compiled[key] = compile_url_param(value)
    return compiled
