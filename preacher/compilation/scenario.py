"""Scenario compilation."""

from __future__ import annotations

from collections.abc import Mapping

from preacher.core.scenario import Scenario
from .error import CompilationError
from .request import compile as compile_request
from .response_description import compile as compile_response_description
from .util import run_on_key


_KEY_LABEL = 'label'
_KEY_REQUEST = 'request'
_KEY_RESPONSE = 'response'


class ScenarioCompiler:
    """
    >>> from unittest.mock import patch, sentinel
    >>> request_patch = patch(
    ...     f'{__name__}.compile_request',
    ...     return_value=sentinel.request,
    ... )
    >>> response_description_patch = patch(
    ...     f'{__name__}.compile_response_description',
    ...     return_value=sentinel.response_description
    ... )

    >>> compiler = ScenarioCompiler()

    >>> with request_patch as request_mock, \\
    ...      response_description_patch as response_description_mock:
    ...     scenario = compiler.compile({})
    ...     request_mock.assert_called_once_with({})
    ...     response_description_mock.assert_called_once_with({})
    >>> scenario.request
    sentinel.request
    >>> scenario.response_description
    sentinel.response_description

    When given a not string label, then raises a compilation error.
    >>> compiler.compile({'label': []})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: Scenario.label ...: label

    When given an invalid type request, then raises a compilation error.
    >>> compiler.compile({'request': []})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: Scenario.request ...: request

    When a request compilation fails, then raises a compilation error.
    >>> with request_patch as request_mock:
    ...     request_mock.side_effect=CompilationError(
    ...         message='message',
    ...         path=['foo'],
    ...     )
    ...     compiler.compile({})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: message: request.foo

    When given an invalid type response description,
    then raises a compilation error.
    >>> with request_patch:
    ...     compiler.compile({'response': 'str'})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: Scenario.response...: response

    When a response description compilation fails,
    then raises a compilation error.
    >>> with request_patch as request_mock, \\
    ...      response_description_patch as response_description_mock:
    ...     response_description_mock.side_effect=CompilationError(
    ...         message='message',
    ...         path=['bar'],
    ...     )
    ...     compiler.compile({'request': '/path'})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: message: response.bar

    Creates a scenario without response description.
    >>> with request_patch as request_mock, \\
    ...      response_description_patch as response_description_mock:
    ...     scenario = compiler.compile({'request': '/path'})
    ...     request_mock.assert_called_once_with('/path')
    >>> scenario.label
    >>> scenario.request
    sentinel.request

    Creates a scenario.
    >>> with request_patch as request_mock, \\
    ...      response_description_patch as response_description_mock:
    ...     scenario = compiler.compile({
    ...         'label': 'label',
    ...         'request': {'path': '/path'},
    ...         'response': {'key': 'value'},
    ...     })
    ...     request_mock.assert_called_once_with({'path': '/path'})
    ...     response_description_mock.assert_called_once_with({'key': 'value'})
    >>> scenario.label
    'label'
    >>> scenario.request
    sentinel.request
    >>> scenario.response_description
    sentinel.response_description
    """
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
        request = run_on_key(_KEY_REQUEST, compile_request, request_obj)

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
