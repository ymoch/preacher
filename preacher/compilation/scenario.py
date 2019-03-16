"""Scenario compilation."""

from preacher.core.scenario import ResponseScenario
from .description import compile as compile_description


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
