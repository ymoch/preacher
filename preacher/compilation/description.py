"""Description compilation."""

from collections.abc import Mapping
from typing import Any

from preacher.core.description import Description, Predicate
from .error import CompilationError
from .predicate import compile as compile_predicate
from .extraction import compile as compile_extraction


def compile(obj: Mapping) -> Description:
    """
    >>> from unittest.mock import patch, sentinel
    >>> extraction_patch = patch(
    ...     f'{__name__}.compile_extraction',
    ...     return_value=sentinel.extraction,
    ... )
    >>> predicate_patch = patch(
    ...     f'{__name__}.compile_predicate',
    ...     return_value=sentinel.predicate,
    ... )

    >>> with extraction_patch as extraction_mock:
    ...     compile({'it': 'str'})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: Description.it ...

    >>> with extraction_patch as extraction_mock:
    ...     compile({'it': [None]})
    Traceback (most recent call last):
        ...
    preacher.compilation.error.CompilationError: Predicate ...

    >>> with extraction_patch as extraction_mock, \\
    ...      predicate_patch as predicate_mock:
    ...     description = compile({
    ...         'it': {'key': 'value'}
    ...     })
    ...     extraction_mock.call_args
    ...     predicate_mock.call_args_list
    call({'it': {'key': 'value'}})
    [call({'key': 'value'})]
    >>> description.extraction
    sentinel.extraction
    >>> description.predicates
    [sentinel.predicate]

    >>> with extraction_patch as extraction_mock, \\
    ...      predicate_patch as predicate_mock:
    ...     description = compile({
    ...         'it': [{'key1': 'value1'}, {'key2': 'value2'}]
    ...     })
    ...     extraction_mock.call_args
    ...     predicate_mock.call_args_list
    call({'it': [{'key1': 'value1'}, {'key2': 'value2'}]})
    [call({'key1': 'value1'}), call({'key2': 'value2'})]
    >>> description.extraction
    sentinel.extraction
    >>> description.predicates
    [sentinel.predicate, sentinel.predicate]
    """
    extraction = compile_extraction(obj)

    predicate_objs = obj.get('it', [])
    if isinstance(predicate_objs, Mapping):
        predicate_objs = [predicate_objs]
    if not isinstance(predicate_objs, list):
        raise CompilationError(
            f'Description.it must be a list or a mapping: {predicate_objs}'
        )

    return Description(
        extraction=extraction,
        predicates=[_compile_predicate(obj) for obj in predicate_objs]
    )


def _compile_predicate(obj: Any) -> Predicate:
    if not isinstance(obj, str) and not isinstance(obj, Mapping):
        raise CompilationError(
            f'Predicate must be a string or a mapping: {obj}'
        )
    return compile_predicate(obj)
