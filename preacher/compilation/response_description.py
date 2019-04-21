"""Response description compilations."""

from collections.abc import Mapping
from typing import Any

from preacher.core.description import Description
from preacher.core.response_description import ResponseDescription
from .error import CompilationError
from .description import compile as compile_description
from .predicate import compile as compile_predicate
from .util import map_on_key


_KEY_STATUS_CODE = 'status_code'
_KEY_BODY = 'body'


def compile(obj: Mapping) -> ResponseDescription:
    """
    >>> from unittest.mock import call, patch, sentinel
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
    ...     predicate_mock.assert_not_called()
    ...     description_mock.assert_not_called()
    >>> response_description.status_code_predicates
    []
    >>> response_description.body_descriptions
    []

    >>> compile({'body': 'str'})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: ...: body

    >>> compile({'body': ['str']})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: Description ...: body[0]

    >>> with predicate_patch as predicate_mock, \\
    ...      description_patch as description_mock:
    ...     response_description = compile({
    ...         'status_code': 402,
    ...         'body': {'key1': 'value1'}}
    ...     )
    ...     predicate_mock.assert_called_once_with(402)
    ...     description_mock.assert_called_once_with({'key1': 'value1'})
    >>> response_description.body_descriptions
    [sentinel.description]

    >>> with predicate_patch as predicate_mock, \\
    ...      description_patch as description_mock:
    ...     response_description = compile({
    ...         'status_code': [{'be_greater_than': 0}, {'be_less_than': 400}],
    ...         'body': [{'key1': 'value1'}, {'key2': 'value2'}],
    ...     })
    ...     predicate_mock.assert_has_calls([
    ...         call({'be_greater_than': 0}),
    ...         call({'be_less_than': 400}),
    ...     ])
    ...     description_mock.assert_has_calls([
    ...         call({'key1': 'value1'}),
    ...         call({'key2': 'value2'}),
    ...     ])
    >>> response_description.body_descriptions
    [sentinel.description, sentinel.description]
    """
    status_code_predicate_objs = obj.get(_KEY_STATUS_CODE, [])
    if not isinstance(status_code_predicate_objs, list):
        status_code_predicate_objs = [status_code_predicate_objs]
    status_code_predicates = list(map_on_key(
        key=_KEY_STATUS_CODE,
        func=compile_predicate,
        items=status_code_predicate_objs,
    ))

    body_description_objs = obj.get(_KEY_BODY, [])
    if isinstance(body_description_objs, Mapping):
        body_description_objs = [body_description_objs]
    if not isinstance(body_description_objs, list):
        raise CompilationError(
            message='ResponseDescription.body must be a list or a mapping',
            path=[_KEY_BODY],
        )
    body_descriptions = list(map_on_key(
        key=_KEY_BODY,
        func=_compile_description,
        items=body_description_objs,
    ))

    return ResponseDescription(
        status_code_predicates=status_code_predicates,
        body_descriptions=body_descriptions,
    )


def _compile_description(obj: Any) -> Description:
    if not isinstance(obj, Mapping):
        raise CompilationError('Description must be a mapping')
    return compile_description(obj)
