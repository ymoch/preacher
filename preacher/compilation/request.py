"""Request compilation."""

from collections.abc import Mapping
from typing import Union

from preacher.core.request import Request
from .error import CompilationError


_KEY_PATH = 'path'
_KEY_PARAMS = 'params'


def compile(obj: Union[Mapping, str]) -> Request:
    """
    >>> compile({'path': {'key': 'value'}})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: Request.path ...: path

    >>> compile({'params': ''})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: Request.params ...: params

    >>> request = compile('/path')
    >>> request.path
    '/path'
    >>> request.params
    {}

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
    if isinstance(obj, str):
        return compile({_KEY_PATH: obj})

    path = obj.get(_KEY_PATH, '')
    if not isinstance(path, str):
        raise CompilationError(
            message=f'Request.{_KEY_PATH} must be a string',
            path=[_KEY_PATH],
        )

    params = obj.get(_KEY_PARAMS, {})
    if not isinstance(params, Mapping):
        raise CompilationError(
            message=f'Request.{_KEY_PARAMS} must be a mapping',
            path=[_KEY_PARAMS],
        )

    return Request(path=path, params=params)
