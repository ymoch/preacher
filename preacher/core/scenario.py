"""Scenario."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .request import Request
from .response_description import (
    ResponseDescription,
    ResponseVerification,
)
from .verification import (
    Status,
    Verification,
    merge_statuses,
)


@dataclass
class ScenarioVerification:
    status: Status
    request: Verification
    response: Optional[ResponseVerification] = None
    label: Optional[str] = None


class Scenario:
    """
    >>> from unittest.mock import MagicMock
    >>> scenario = Scenario(
    ...     request=MagicMock(Request, side_effect=RuntimeError('message')),
    ...     response_description=MagicMock(ResponseDescription),
    ... )
    >>> scenario.label
    >>> verification = scenario('base-url')
    >>> scenario.request.call_args
    call('base-url')
    >>> scenario.response_description.call_count
    0
    >>> verification.label
    >>> verification.status.name
    'FAILURE'
    >>> verification.request.status.name
    'FAILURE'
    >>> verification.request.message
    'RuntimeError: message'

    >>> from .request import Response
    >>> inner_response = MagicMock(Response, status_code=402, body='body')
    >>> scenario = Scenario(
    ...     label='Response should be unstable',
    ...     request=MagicMock(Request, return_value=inner_response),
    ...     response_description=MagicMock(
    ...         ResponseDescription,
    ...         return_value=ResponseVerification(
    ...             status=Status.UNSTABLE,
    ...             status_code=Verification.succeed(),
    ...             body=Verification(status=Status.UNSTABLE)
    ...         ),
    ...     ),
    ... )
    >>> verification = scenario('base-url')
    >>> scenario.response_description.call_args
    call(body='body', status_code=402)
    >>> verification.label
    'Response should be unstable'
    >>> verification.status.name
    'UNSTABLE'
    >>> verification.request.status.name
    'SUCCESS'
    >>> verification.response.status.name
    'UNSTABLE'
    >>> verification.response.body.status.name
    'UNSTABLE'
    """
    def __init__(
        self: Scenario,
        request: Request,
        response_description: ResponseDescription,
        label: Optional[str] = None,
    ) -> None:
        self._label = label
        self._request = request
        self._response_description = response_description

    def __call__(self: Scenario, base_url: str) -> ScenarioVerification:
        try:
            response = self._request(base_url)
        except Exception as error:
            return ScenarioVerification(
                status=Status.FAILURE,
                request=Verification.of_error(error),
            )
        request_verification = Verification.succeed()

        response_verification = self._response_description(
            status_code=response.status_code,
            body=response.body,
        )

        status = merge_statuses([
            request_verification.status,
            response_verification.status,
        ])
        return ScenarioVerification(
            status=status,
            request=request_verification,
            response=response_verification,
            label=self._label,
        )

    @property
    def label(self: Scenario) -> Optional[str]:
        return self._label

    @property
    def request(self: Scenario) -> Request:
        return self._request

    @property
    def response_description(self: Scenario) -> ResponseDescription:
        return self._response_description
