"""Case compilation."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Optional

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
    preacher.compilation.error.CompilationError: Case.label ...: label

    When given an invalid type request, then raises a compilation error.
    >>> compiler = CaseCompiler()
    >>> compiler.compile({'request': []})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: Case.request ...: request

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
    preacher.compilation.error.CompilationError: Case.response...: response

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

    def compile(self: CaseCompiler, obj: Mapping) -> Case:
        label = obj.get(_KEY_LABEL)
        if label is not None and not isinstance(label, str):
            raise CompilationError(
                message=f'Case.{_KEY_LABEL} must be a string',
                path=[_KEY_LABEL],
            )

        request_obj = obj.get(_KEY_REQUEST, {})
        if (
            not isinstance(request_obj, Mapping)
            and not isinstance(request_obj, str)
        ):
            raise CompilationError(
                message=(
                    f'Case.{_KEY_REQUEST} must be a string or a mapping'
                ),
                path=[_KEY_REQUEST],
            )
        request = run_on_key(
            _KEY_REQUEST,
            self._request_compiler.compile,
            request_obj,
        )

        response_obj = obj.get('response', {})
        if not isinstance(response_obj, Mapping):
            raise CompilationError(
                message=f'Case.{_KEY_RESPONSE} object must be a mapping',
                path=[_KEY_RESPONSE],
            )
        response_description = run_on_key(
            _KEY_RESPONSE,
            self._response_compiler.compile,
            response_obj,
        )

        return Case(
            label=label,
            request=request,
            response_description=response_description,
        )
