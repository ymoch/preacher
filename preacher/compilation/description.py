"""Description compilation."""

from collections.abc import Mapping
from typing import Any

from preacher.core.description import Description, Predicate
from .error import CompilationError
from .predicate import compile as compile_predicate
from .extraction import compile as compile_extraction


def compile(obj: Mapping) -> Description:
    """
    >>> description = compile({
    ...     'jq': '.foo',
    ...     'it': {'ends_with': 'r'},
    ... })
    >>> description({}).status.name
    'UNSTABLE'
    >>> description({'foo': 'bar'}).status.name
    'SUCCESS'
    >>> description({'foo': 'baz'}).status.name
    'UNSTABLE'

    >>> description = compile({
    ...     'jq': '.foo',
    ...     'it': [
    ...         {'starts_with': 'b'},
    ...         {'ends_with': 'z'},
    ...     ],
    ... })
    >>> description({}).status.name
    'UNSTABLE'
    >>> description({'foo': 'bar'}).status.name
    'UNSTABLE'
    >>> description({'foo': 'baz'}).status.name
    'SUCCESS'
    """
    extraction = compile_extraction(obj)

    predicate_objs = obj.get('it', [])
    if isinstance(predicate_objs, Mapping):
        predicate_objs = [predicate_objs]
    if not isinstance(predicate_objs, list):
        raise CompilationError(
            'Description.predicates must be a list or an object'
            f': {predicate_objs}'
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
