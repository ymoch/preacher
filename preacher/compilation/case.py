"""Case compilation."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Optional, Union

from preacher.core.case import Case
from .error import CompilationError
from .request import RequestCompiler
from .response_description import ResponseDescriptionCompiler
from .util import run_on_key


_KEY_LABEL = 'label'
_KEY_REQUEST = 'request'
_KEY_RESPONSE = 'response'


class CaseCompiler:
    """
    >>> from unittest.mock import MagicMock, sentinel
    >>> def default_request_compiler() -> RequestCompiler:
    ...     return MagicMock(
    ...         spec=RequestCompiler,
    ...         compile=MagicMock(return_value=sentinel.request),
    ...     )
    >>> def default_response_compiler() -> ResponseDescriptionCompiler:
    ...     return MagicMock(
    ...         spec=ResponseDescriptionCompiler,
    ...         compile=MagicMock(return_value=sentinel.response_description),
    ...     )

    When given an empty object, then generates a default case.
    >>> request_compiler = default_request_compiler()
    >>> response_compiler = default_response_compiler()
    >>> compiler = CaseCompiler(request_compiler, response_compiler)
    >>> case = compiler.compile({})
    >>> case.request
    sentinel.request
    >>> case.response_description
    sentinel.response_description
    >>> request_compiler.compile.assert_called_once_with({})
    >>> response_compiler.compile.assert_called_once_with({})

    When given a not string label, then raises a compilation error.
    >>> compiler = CaseCompiler()
    >>> compiler.compile({'label': []})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ...: label

    When given an invalid type request, then raises a compilation error.
    >>> compiler = CaseCompiler()
    >>> compiler.compile({'request': []})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ...: request

    When a request compilation fails, then raises a compilation error.
    >>> request_compiler = MagicMock(
    ...     spec=RequestCompiler,
    ...     compile=MagicMock(
    ...         side_effect=CompilationError(message='message', path=['foo'])
    ...     ),
    ... )
    >>> compiler = CaseCompiler(request_compiler)
    >>> compiler.compile({})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: message: request.foo

    When given an invalid type response description,
    then raises a compilation error.
    >>> request_compiler = default_request_compiler()
    >>> compiler = CaseCompiler(request_compiler)
    >>> compiler.compile({'response': 'str'})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ...: response

    When a response description compilation fails,
    then raises a compilation error.
    >>> request_compiler = default_request_compiler()
    >>> response_compiler = MagicMock(
    ...     spec=ResponseDescriptionCompiler,
    ...     compile=MagicMock(
    ...         side_effect=CompilationError(message='message', path=['bar']),
    ...     ),
    ... )
    >>> compiler = CaseCompiler(request_compiler, response_compiler)
    >>> compiler.compile({'request': '/path'})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: message: response.bar

    Creates a case only with a request.
    >>> request_compiler = default_request_compiler()
    >>> response_compiler = default_response_compiler()
    >>> compiler = CaseCompiler(request_compiler, response_compiler)
    >>> case = compiler.compile({'request': '/path'})
    >>> case.label
    >>> case.request
    sentinel.request
    >>> request_compiler.compile.assert_called_once_with('/path')

    Creates a case.
    >>> request_compiler = default_request_compiler()
    >>> response_compiler = default_response_compiler()
    >>> compiler = CaseCompiler(request_compiler, response_compiler)
    >>> case = compiler.compile({
    ...     'label': 'label',
    ...     'request': {'path': '/path'},
    ...     'response': {'key': 'value'},
    ... })
    >>> case.label
    'label'
    >>> case.request
    sentinel.request
    >>> case.response_description
    sentinel.response_description
    >>> request_compiler.compile.assert_called_once_with({'path': '/path'})
    >>> response_compiler.compile.assert_called_once_with({'key': 'value'})

    When given invalid default request, then raises a compilation error.
    >>> case_compiler = CaseCompiler()
    >>> case_compiler.of_default({'request': []})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ...: request

    Accepts default values.
    >>> request_compiler = MagicMock(
    ...     RequestCompiler,
    ...     of_default=MagicMock(return_value=sentinel.foo),
    ... )
    >>> response_compiler = default_response_compiler()
    >>> compiler = CaseCompiler(request_compiler, response_compiler)
    >>> default_compiler = compiler.of_default({})
    >>> default_compiler.request_compiler
    sentinel.foo
    """
    def __init__(
        self: CaseCompiler,
        request_compiler: Optional[RequestCompiler] = None,
        response_compiler: Optional[ResponseDescriptionCompiler] = None
    ) -> None:
        self._request_compiler = request_compiler or RequestCompiler()
        self._response_compiler = (
            response_compiler or ResponseDescriptionCompiler()
        )

    @property
    def request_compiler(self: CaseCompiler) -> RequestCompiler:
        return self._request_compiler

    def compile(self: CaseCompiler, obj: Mapping) -> Case:
        label = obj.get(_KEY_LABEL)
        if label is not None and not isinstance(label, str):
            raise CompilationError(
                message=f'Case.{_KEY_LABEL} must be a string',
                path=[_KEY_LABEL],
            )

        request = run_on_key(
            _KEY_REQUEST,
            self._request_compiler.compile,
            _extract_request(obj)
        )
        response_description = run_on_key(
            _KEY_RESPONSE,
            self._response_compiler.compile,
            _extract_response(obj),
        )
        return Case(
            label=label,
            request=request,
            response_description=response_description,
        )

    def of_default(self: CaseCompiler, obj: Mapping) -> CaseCompiler:
        request_compiler = run_on_key(
            _KEY_REQUEST,
            self._request_compiler.of_default,
            _extract_request(obj),
        )
        return CaseCompiler(request_compiler=request_compiler)


def _extract_request(obj: Any) -> Union[Mapping, str]:
    target = obj.get(_KEY_REQUEST, {})
    if not isinstance(target, Mapping) and not isinstance(target, str):
        raise CompilationError(
            message='must be a string or a mapping',
            path=[_KEY_REQUEST],
        )
    return target


def _extract_response(obj: Any) -> Mapping:
    target = obj.get('response', {})
    if not isinstance(target, Mapping):
        raise CompilationError('must be a mapping', path=[_KEY_RESPONSE])
    return target
