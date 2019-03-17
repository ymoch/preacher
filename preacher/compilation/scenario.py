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
    >>> from unittest.mock import patch, sentinel
    >>> description_patch = patch(
    ...     f'{__name__}.compile_description',
    ...     return_value=sentinel.description,
    ... )

    >>> with description_patch as description_mock:
    ...     response_scenario = compile_response_scenario({})
    ...     description_mock.call_args_list
    []
    >>> response_scenario.body_descriptions
    []

    >>> compile_response_scenario({'body': 'str'})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ResponseScenario.body ...

    >>> compile_response_scenario({'body': ['str']})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: Description ...

    >>> with description_patch as description_mock:
    ...     response_scenario = compile_response_scenario({
    ...        'body': {'key1': 'value1'},
    ...     })
    ...     description_mock.call_args_list
    [call({'key1': 'value1'})]
    >>> response_scenario.body_descriptions
    [sentinel.description]

    >>> with description_patch as description_mock:
    ...     response_scenario = compile_response_scenario({
    ...         'body': [{'key1': 'value1'}, {'key2': 'value2'}],
    ...     })
    ...     description_mock.call_args_list
    [call({'key1': 'value1'}), call({'key2': 'value2'})]
    >>> response_scenario.body_descriptions
    [sentinel.description, sentinel.description]
    """
    body_description_objs = obj.get('body', [])
    if isinstance(body_description_objs, Mapping):
        body_description_objs = [body_description_objs]
    if not isinstance(body_description_objs, list):
        raise CompilationError(
            'ResponseScenario.body must be a list or a mapping'
            f': {body_description_objs}'
        )
    body_descriptions = [
        _compile_description(body_description_obj)
        for body_description_obj in body_description_objs
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
