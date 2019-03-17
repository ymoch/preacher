"""Scenario compilation."""

from collections.abc import Mapping

from preacher.core.scenario import ResponseScenario, Scenario
from .error import CompilationError
from .description import compile as compile_description
from .request import compile as compile_request


def compile_response_scenario(obj: Mapping) -> ResponseScenario:
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


def compile_scenario(obj: Mapping) -> Scenario:
    """
    >>> from unittest.mock import patch
    """
    request_obj = obj.get('request', {})
    if not isinstance(request_obj, Mapping):
        raise CompilationError(
            f'Request object must be mapping: {request_obj}'
        )
    request = compile_request(obj.get('request', {}))

    response_obj = obj.get('response', {})
    if not isinstance(response_obj, Mapping):
        raise CompilationError(
            f'ResponseScenario object must be mapping: {response_obj}'
        )
    response_scenario = compile_response_scenario(response_obj)

    return Scenario(request=request, response_scenario=response_scenario)
