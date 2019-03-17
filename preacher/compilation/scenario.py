"""Scenario compilation."""

from preacher.core.scenario import ResponseScenario, Scenario
from .description import compile as compile_description
from .request import compile as compile_request


def compile_response_scenario(obj: dict) -> ResponseScenario:
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
        for description_object in obj.get('body', [])
    ]
    return ResponseScenario(body_descriptions)


def compile_scenario(obj: dict) -> Scenario:
    """
    """
    request = compile_request(obj.get('request', {}))
    response_scenario = compile_response_scenario(obj.get('response', {}))
    return Scenario(request=request, response_scenario=response_scenario)
