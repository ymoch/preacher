"""Scenario compilation."""

from collections.abc import Mapping

from preacher.core.scenario import Scenario
from .error import CompilationError
from .request import compile as compile_request
from .response_description import compile as compile_response_description


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
    ...     request_mock.call_args
    ...     response_description_mock.call_args
    call({})
    call({})
    >>> scenario.request
    sentinel.request
    >>> scenario.response_description
    sentinel.response_description

    >>> compile_scenario({'label': []})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: Scenario.label ...

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
    ...      response_description_patch as response_description_mock:
    ...     scenario = compile_scenario({'request': '/path'})
    ...     request_mock.call_args
    call({'path': '/path'})
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
    ...     request_mock.call_args
    ...     response_description_mock.call_args
    call({'path': '/path'})
    call({'key': 'value'})
    >>> scenario.label
    'label'
    >>> scenario.request
    sentinel.request
    >>> scenario.response_description
    sentinel.response_description
    """
    label = obj.get('label')
    if label is not None and not isinstance(label, str):
        raise CompilationError(f'Scenario.label must be a string: {label}')

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
    response_description = compile_response_description(response_obj)

    return Scenario(
        label=label,
        request=request,
        response_description=response_description,
    )
