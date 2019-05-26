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
    """
    When given not a string path, then raises a compiration error.
    >>> compiler = RequestCompiler()
    >>> compiler.compile({'path': {'key': 'value'}})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ...: path
    >>> compiler.of_default({'path': {'key': 'value'}})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ...: path

    When given not a mapping parameters, then raises a compilation error.
    >>> compiler = RequestCompiler()
    >>> compiler.compile({'params': ''})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ...: params
    >>> compiler.of_default({'params': ''})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ...: params

    When given an empty mapping, then returns the dafault mapping..
    >>> compiler = RequestCompiler()
    >>> request = compiler.compile({})
    >>> request.path
    ''
    >>> request.params
    {}

    When given a string, then returns a request of the path.
    >>> compiler = RequestCompiler()
    >>> request = compiler.compile('/path')
    >>> request.path
    '/path'
    >>> request.params
    {}
    >>> compiler = compiler.of_default('/default-path')
    >>> request = compiler.compile({'params': {'k': 'v'}})
    >>> request.path
    '/default-path'
    >>> request.params
    {'k': 'v'}

    When given a filled mapping, then returns the request of it.
    >>> compiler = RequestCompiler()
    >>> request = compiler.compile(
    ...     {'path': '/path', 'params': {'key': 'value'}}
    ... )
    >>> request.path
    '/path'
    >>> request.params
    {'key': 'value'}
    >>> compiler = compiler.of_default({
    ...     'path': '/default-path',
    ...     'params': {'k': 'v'},
    ... })
    >>> request = compiler.compile({})
    >>> request.path
    '/default-path'
    >>> request.params
    {'k': 'v'}
    >>> request = compiler.compile('/path')
    >>> request.path
    '/path'
    >>> request.params
    {'k': 'v'}
    >>> request = compiler.compile(
    ...     {'path': '/path', 'params': {'key': 'value'}}
    ... )
    >>> request.path
    '/path'
    >>> request.params
    {'key': 'value'}
    """
    def __init__(
        self: RequestCompiler,
        path: str = '',
        params: Mapping = {},
    ) -> None:
        self._path = path
        self._params = params

    def compile(self: RequestCompiler, obj: Union[Mapping, str]) -> Request:
        compiled = _compile(obj)
        return compiled.to_request(
            default_path=self._path,
            default_params=self._params,
        )

    def of_default(
        self: RequestCompiler,
        obj: Union[Mapping, str],
    ) -> RequestCompiler:
        compiled = _compile(obj)
        return RequestCompiler(
            path=or_default(compiled.path, self._path),
            params=or_default(compiled.params, self._params),
        )
