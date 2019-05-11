"""Scenario compilation."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Optional

from preacher.core.scenario import Scenario
from .error import CompilationError
from .request import RequestCompiler
from .response_description import compile as compile_response_description
from .util import run_on_key


_KEY_LABEL = 'label'
_KEY_REQUEST = 'request'
_KEY_RESPONSE = 'response'


class ScenarioCompiler:
    """
    >>> from unittest.mock import MagicMock, patch, sentinel
    >>> request_compiler_ctor_patch = patch(f'{__name__}.RequestCompiler')
    >>> response_description_patch = patch(
    ...     f'{__name__}.compile_response_description',
    ...     return_value=sentinel.response_description
    ... )

    >>> def default_request_compiler() -> RequestCompiler:
    ...     return MagicMock(
    ...         spec=RequestCompiler,
    ...         compile=MagicMock(return_value=sentinel.request),
    ...     )

    When given an empty object, then generates a default scenario.
    >>> request_compiler = default_request_compiler()
    >>> compiler = ScenarioCompiler(request_compiler)
    >>> with response_description_patch as response_description_mock:
    ...     scenario = compiler.compile({})
    ...     response_description_mock.assert_called_once_with({})
    >>> request_compiler.compile.assert_called_once_with({})
    >>> scenario.request
    sentinel.request
    >>> scenario.response_description
    sentinel.response_description

    When given a not string label, then raises a compilation error.
    >>> compiler = ScenarioCompiler()
    >>> compiler.compile({'label': []})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: Scenario.label ...: label

    When given an invalid type request, then raises a compilation error.
    >>> compiler = ScenarioCompiler()
    >>> compiler.compile({'request': []})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: Scenario.request ...: request

    When a request compilation fails, then raises a compilation error.
    >>> request_compiler = MagicMock(
    ...     spec=RequestCompiler,
    ...     compile=MagicMock(
    ...         side_effect=CompilationError(message='message', path=['foo'])
    ...     ),
    ... )
    >>> compiler = ScenarioCompiler(request_compiler)
    >>> compiler.compile({})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: message: request.foo

    When given an invalid type response description,
    then raises a compilation error.
    >>> request_compiler = default_request_compiler()
    >>> compiler = ScenarioCompiler(request_compiler)
    >>> compiler.compile({'response': 'str'})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: Scenario.response...: response

    When a response description compilation fails,
    then raises a compilation error.
    >>> request_compiler = default_request_compiler()
    >>> compiler = ScenarioCompiler(request_compiler)
    >>> with response_description_patch as response_description_mock:
    ...     response_description_mock.side_effect=CompilationError(
    ...         message='message',
    ...         path=['bar'],
    ...     )
    ...     compiler.compile({'request': '/path'})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: message: response.bar

    Creates a scenario only with a request.
    >>> request_compiler = default_request_compiler()
    >>> compiler = ScenarioCompiler(request_compiler)
    >>> with response_description_patch as response_description_mock:
    ...     scenario = compiler.compile({'request': '/path'})
    >>> request_compiler.compile.assert_called_once_with('/path')
    >>> scenario.label
    >>> scenario.request
    sentinel.request

    Creates a scenario.
    >>> request_compiler.compile.reset_mock()
    >>> request_compiler = default_request_compiler()
    >>> compiler = ScenarioCompiler(request_compiler)
    >>> with response_description_patch as response_description_mock:
    ...     scenario = compiler.compile({
    ...         'label': 'label',
    ...         'request': {'path': '/path'},
    ...         'response': {'key': 'value'},
    ...     })
    ...     response_description_mock.assert_called_once_with({'key': 'value'})
    >>> request_compiler.compile.assert_called_once_with({'path': '/path'})
    >>> scenario.label
    'label'
    >>> scenario.request
    sentinel.request
    >>> scenario.response_description
    sentinel.response_description
    """
    def __init__(
        self: ScenarioCompiler,
        request_compiler: Optional[RequestCompiler] = None,
    ) -> None:
        self._request_compiler = request_compiler or RequestCompiler()

    def compile(self: ScenarioCompiler, obj: Mapping) -> Scenario:
        label = obj.get(_KEY_LABEL)
        if label is not None and not isinstance(label, str):
            raise CompilationError(
                message=f'Scenario.{_KEY_LABEL} must be a string',
                path=[_KEY_LABEL],
            )

        request_obj = obj.get(_KEY_REQUEST, {})
        if (
            not isinstance(request_obj, Mapping)
            and not isinstance(request_obj, str)
        ):
            raise CompilationError(
                message=(
                    f'Scenario.{_KEY_REQUEST} must be a string or a mapping'
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
                message=f'Scenario.{_KEY_RESPONSE} object must be a mapping',
                path=[_KEY_RESPONSE],
            )
        response_description = run_on_key(
            _KEY_RESPONSE,
            compile_response_description,
            response_obj,
        )

        return Scenario(
            label=label,
            request=request,
            response_description=response_description,
        )
