"""Request compilation."""

from collections.abc import Mapping
from preacher.core.request import Request
from .error import CompilationError


def compile(obj: Mapping) -> Request:
    """
    >>> compile({'path': {'key': 'value'}})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: Request.path ...

    >>> compile({'params': ''})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: Request.params ...

    >>> request = compile({})
    >>> request.path
    ''
    >>> request.params
    {}

    >>> request = compile({'path': '/path', 'params': {'key': 'value'}})
    >>> request.path
    '/path'
    >>> request.params
    {'key': 'value'}
    """
    path = obj.get('path', '')
    if not isinstance(path, str):
        raise CompilationError(f'Request.path must be a string: {path}')

    params = obj.get('params', {})
    if not isinstance(params, Mapping):
        raise CompilationError(f'Request.params must be a mapping: {params}')

    return Request(path=path, params=params)
