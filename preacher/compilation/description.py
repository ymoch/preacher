"""Description compilation."""

from preacher.core.description import Description
from .predicate import compile as compile_predicate
from .extraction import compile as compile_extraction


def compile(obj: dict) -> Description:
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
    predicate_objects = obj.get('it', [])
    if isinstance(predicate_objects, dict):
        predicate_objects = [predicate_objects]
    return Description(
        extraction=extraction,
        predicates=[compile_predicate(obj) for obj in predicate_objects]
    )
