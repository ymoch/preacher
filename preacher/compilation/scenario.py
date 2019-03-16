"""Scenario compilation."""

from preacher.core.scenario import (
    ResponseScenario,
    Description,
)
from .predicate import compile as compile_predicate
from .extraction import compile as compile_extraction


def compile_description(description_object: dict) -> Description:
    """
    >>> description = compile_description({
    ...     'jq': '.foo',
    ...     'it': {'ends_with': 'r'},
    ... })
    >>> description({}).status.name
    'UNSTABLE'
    >>> description({'foo': 'bar'}).status.name
    'SUCCESS'
    >>> description({'foo': 'baz'}).status.name
    'UNSTABLE'

    >>> description = compile_description({
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
    extraction = compile_extraction(description_object)
    predicate_objects = description_object.get('it', [])
    if isinstance(predicate_objects, dict):
        predicate_objects = [predicate_objects]
    return Description(
        extraction=extraction,
        predicates=[compile_predicate(obj) for obj in predicate_objects]
    )


def compile_response_scenario(response_object: dict) -> ResponseScenario:
    """
    >>> scenario = compile_response_scenario({})
    >>> verification = scenario(body=b'{}')
    >>> verification.body.status.name
    'SUCCESS'
    >>> verification.body.children
    []
    """
    body_descriptions = [
        compile_description(description_object)
        for description_object in response_object.get('body', [])
    ]
    return ResponseScenario(body_descriptions)
