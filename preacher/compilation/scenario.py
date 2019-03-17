"""Scenario compilation."""

from collections.abc import Mapping
from typing import Any

from preacher.core.description import Description
from preacher.core.scenario import ResponseScenario, Scenario
from .error import CompilationError
from .description import compile as compile_description
from .request import compile as compile_request


def compile_response_scenario(obj: Mapping) -> ResponseScenario:
    """
    >>> scenario = compile_response_scenario({})
    >>> verification = scenario(body='{}')
    >>> verification.body.status.name
    'SUCCESS'
    >>> verification.body.children
    []
    """
    body_descriptions = [
        _compile_description(description_obj)
        for description_obj in obj.get('body', [])
    ]
    return ResponseScenario(
        body_descriptions=body_descriptions,
    )


def compile_scenario(obj: Mapping) -> Scenario:
    """
    >>> from unittest.mock import patch, sentinel
    >>> request_patch = patch(
    ...     f'{__name__}.compile_request',
    ...     return_value=sentinel.request,
    ... )
    >>> response_scenario_patch = patch(
    ...     f'{__name__}.compile_response_scenario',
    ...     return_value=sentinel.response_scenario
    ... )

    >>> with request_patch as request_mock, \\
    ...      response_scenario_patch as response_scenario_mock:
    ...     scenario = compile_scenario({})
    ...     request_mock.call_args
    ...     response_scenario_mock.call_args
    call({})
    call({})
    >>> scenario.request
    sentinel.request
    >>> scenario.response_scenario
    sentinel.response_scenario

    >>> compile_scenario({'request': []})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: Scenario.request ...

    >>> with request_patch:
    ...     compile_scenario({'response': 'str'})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: Scenario.response ...

    >>> with request_patch as request_mock, \\
    ...      response_scenario_patch as response_scenario_mock:
    ...     scenario = compile_scenario({'request': '/path'})
    ...     request_mock.call_args
    call({'path': '/path'})
    >>> scenario.request
    sentinel.request

    >>> with request_patch as request_mock, \\
    ...      response_scenario_patch as response_scenario_mock:
    ...     scenario = compile_scenario({
    ...         'request': {'path': '/path'},
    ...         'response': {'key': 'value'},
    ...     })
    ...     request_mock.call_args
    ...     response_scenario_mock.call_args
    call({'path': '/path'})
    call({'key': 'value'})
    >>> scenario.request
    sentinel.request
    >>> scenario.response_scenario
    sentinel.response_scenario
    """
    request_obj = obj.get('request', {})
    if isinstance(request_obj, str):
        request_obj = {'path': request_obj}
    if not isinstance(request_obj, Mapping):
        raise CompilationError(
            f'Scenario.request must be a string or a mapping: {request_obj}'
        )
    request = compile_request(request_obj)

    response_obj = obj.get('response', {})
    if not isinstance(response_obj, Mapping):
        raise CompilationError(
            f'Scenario.response object must be a mapping: {response_obj}'
        )
    response_scenario = compile_response_scenario(response_obj)

    return Scenario(request=request, response_scenario=response_scenario)


def _compile_description(obj: Any) -> Description:
    if not isinstance(obj, Mapping):
        raise CompilationError(
            f'Description must be a mapping: {obj}'
        )
    return compile_description(obj)
