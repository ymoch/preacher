"""Request compilation."""

from collections.abc import Mapping
from preacher.core.request import Request
from .error import CompilationError


def compile(obj: Mapping) -> Request:
    """
    >>> request = compile({})
    """
    path = obj.get('path', '')
    if not isinstance(path, str):
        raise CompilationError(f'Path must be a string: {path}')

    params = obj.get('params', {})
    if not isinstance(params, Mapping):
        raise CompilationError(f'Parameters must be a mapping: {params}')

    return Request(path=path, params=params)
