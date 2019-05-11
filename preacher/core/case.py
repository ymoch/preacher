"""Test case."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .request import Request
from .response_description import (
    ResponseDescription,
    ResponseVerification,
)
from .status import Status, merge_statuses
from .verification import Verification


@dataclass
class CaseResult:
    status: Status
    request: Verification
    response: Optional[ResponseVerification] = None
    label: Optional[str] = None


class Case:
    """
    >>> from unittest.mock import MagicMock
    >>> case = Case(
    ...     request=MagicMock(Request, side_effect=RuntimeError('message')),
    ...     response_description=MagicMock(ResponseDescription),
    ... )
    >>> case.label
    >>> verification = case('base-url')
    >>> case.request.call_args
    call('base-url')
    >>> case.response_description.call_count
    0
    >>> verification.label
    >>> verification.status
    FAILURE
    >>> verification.request.status
    FAILURE
    >>> verification.request.message
    'RuntimeError: message'

    >>> from .request import Response
    >>> inner_response = MagicMock(Response, status_code=402, body='body')
    >>> case = Case(
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
    >>> verification = case('base-url')
    >>> case.response_description.call_args
    call(body='body', status_code=402)
    >>> verification.label
    'Response should be unstable'
    >>> verification.status
    UNSTABLE
    >>> verification.request.status
    SUCCESS
    >>> verification.response.status
    UNSTABLE
    >>> verification.response.body.status
    UNSTABLE
    """
    def __init__(
        self: Case,
        request: Request,
        response_description: ResponseDescription,
        label: Optional[str] = None,
    ) -> None:
        self._label = label
        self._request = request
        self._response_description = response_description

    def __call__(self: Case, base_url: str) -> CaseResult:
        try:
            response = self._request(base_url)
        except Exception as error:
            return CaseResult(
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
        return CaseResult(
            status=status,
            request=request_verification,
            response=response_verification,
            label=self._label,
        )

    @property
    def label(self: Case) -> Optional[str]:
        return self._label

    @property
    def request(self: Case) -> Request:
        return self._request

    @property
    def response_description(self: Case) -> ResponseDescription:
        return self._response_description
