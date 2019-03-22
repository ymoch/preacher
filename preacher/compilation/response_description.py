"""Response description compilations."""

from collections.abc import Mapping
from typing import Any

from preacher.core.description import Description
from preacher.core.response_description import ResponseDescription
from .description import compile as compile_description
from .error import CompilationError


def compile(obj: Mapping) -> ResponseDescription:
    """
    >>> from unittest.mock import patch, sentinel
    >>> description_patch = patch(
    ...     f'{__name__}.compile_description',
    ...     return_value=sentinel.description,
    ... )

    >>> with description_patch as description_mock:
    ...     response_scenario = compile({})
    ...     description_mock.call_args_list
    []
    >>> response_scenario.body_descriptions
    []

    >>> compile({'body': 'str'})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ResponseDescription.body ...

    >>> compile({'body': ['str']})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: Description ...

    >>> with description_patch as description_mock:
    ...     response_scenario = compile({'body': {'key1': 'value1'}})
    ...     description_mock.call_args_list
    [call({'key1': 'value1'})]
    >>> response_scenario.body_descriptions
    [sentinel.description]

    >>> with description_patch as description_mock:
    ...     response_scenario = compile({
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
            'ResponseDescription.body must be a list or a mapping'
            f': {body_description_objs}'
        )
    body_descriptions = [
        _compile_description(body_description_obj)
        for body_description_obj in body_description_objs
    ]

    return ResponseDescription(
        status_code_predicates=[],  # TODO: implement here.
        body_descriptions=body_descriptions,
    )


def _compile_description(obj: Any) -> Description:
    if not isinstance(obj, Mapping):
        raise CompilationError(
            f'Description must be a mapping: {obj}'
        )
    return compile_description(obj)
