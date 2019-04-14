"""Scenario compilation."""

from collections.abc import Mapping

from preacher.core.scenario import Scenario
from .error import CompilationError
from .request import compile as compile_request
from .response_description import compile as compile_response_description
from .util import run_on_key


_KEY_LABEL = 'label'
_KEY_REQUEST = 'request'
_KEY_RESPONSE = 'response'


def compile_scenario(obj: Mapping) -> Scenario:
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

    >>> with request_patch as request_mock, \\
    ...      response_description_patch as response_description_mock:
    ...     scenario = compile_scenario({})
    ...     request_mock.assert_called_once_with({})
    ...     response_description_mock.assert_called_once_with({})
    >>> scenario.request
    sentinel.request
    >>> scenario.response_description
    sentinel.response_description

    >>> compile_scenario({'label': []})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: Scenario.label ...: label

    >>> compile_scenario({'request': []})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: Scenario.request ...: request

    >>> with request_patch as request_mock:
    ...     request_mock.side_effect=CompilationError(
    ...         message='message',
    ...         path=['foo'],
    ...     )
    ...     compile_scenario({})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: message: request.foo

    >>> with request_patch:
    ...     compile_scenario({'response': 'str'})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: Scenario.response...: response

    >>> with request_patch as request_mock, \\
    ...      response_description_patch as response_description_mock:
    ...     response_description_mock.side_effect=CompilationError(
    ...         message='message',
    ...         path=['bar'],
    ...     )
    ...     scenario = compile_scenario({'request': '/path'})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: message: response.bar

    >>> with request_patch as request_mock, \\
    ...      response_description_patch as response_description_mock:
    ...     scenario = compile_scenario({'request': '/path'})
    ...     request_mock.assert_called_once_with('/path')
    >>> scenario.label
    >>> scenario.request
    sentinel.request

    >>> with request_patch as request_mock, \\
    ...      response_description_patch as response_description_mock:
    ...     scenario = compile_scenario({
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
            message=f'Scenario.{_KEY_REQUEST} must be a string or a mapping',
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
