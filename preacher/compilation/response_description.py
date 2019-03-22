"""Response description compilations."""

from collections.abc import Mapping
from typing import Any

from preacher.core.description import Description
from preacher.core.response_description import ResponseDescription
from .error import CompilationError
from .description import compile as compile_description
from .predicate import compile as compile_predicate


def compile(obj: Mapping) -> ResponseDescription:
    """
    >>> from unittest.mock import patch, sentinel
    >>> predicate_patch = patch(
    ...     f'{__name__}.compile_predicate',
    ...     return_value=sentinel.predicate,
    ... )
    >>> description_patch = patch(
    ...     f'{__name__}.compile_description',
    ...     return_value=sentinel.description,
    ... )

    >>> with predicate_patch as predicate_mock, \\
    ...      description_patch as description_mock:
    ...     response_description = compile({})
    ...     assert predicate_mock.call_count == 0
    ...     assert description_mock.call_count == 0
    >>> response_description.status_code_predicates
    []
    >>> response_description.body_descriptions
    []

    >>> compile({'body': 'str'})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ResponseDescription.body ...

    >>> compile({'body': ['str']})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: Description ...

    >>> with predicate_patch as predicate_mock, \\
    ...      description_patch as description_mock:
    ...     response_description = compile({
    ...         'status_code': 402,
    ...         'body': {'key1': 'value1'}}
    ...     )
    ...     predicate_mock.call_args_list
    ...     description_mock.call_args_list
    [call({'equals_to': 402})]
    [call({'key1': 'value1'})]
    >>> response_description.body_descriptions
    [sentinel.description]

    >>> with predicate_patch as predicate_mock, \\
    ...      description_patch as description_mock:
    ...     response_description = compile({
    ...         'status_code': [{'is_greater_than': 0}, {'is_less_than': 400}],
    ...         'body': [{'key1': 'value1'}, {'key2': 'value2'}],
    ...     })
    ...     predicate_mock.call_args_list
    ...     description_mock.call_args_list
    [call({'is_greater_than': 0}), call({'is_less_than': 400})]
    [call({'key1': 'value1'}), call({'key2': 'value2'})]
    >>> response_description.body_descriptions
    [sentinel.description, sentinel.description]
    """
    status_code_predicate_objs = obj.get('status_code', [])
    if isinstance(status_code_predicate_objs, int):
        status_code_predicate_objs = {'equals_to': status_code_predicate_objs}
    if not isinstance(status_code_predicate_objs, list):
        status_code_predicate_objs = [status_code_predicate_objs]
    status_code_predicates = [
        compile_predicate(obj) for obj in status_code_predicate_objs
    ]

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
        status_code_predicates=status_code_predicates,
        body_descriptions=body_descriptions,
    )


def _compile_description(obj: Any) -> Description:
    if not isinstance(obj, Mapping):
        raise CompilationError(
            f'Description must be a mapping: {obj}'
        )
    return compile_description(obj)
