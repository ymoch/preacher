"""Test case."""

from dataclasses import dataclass
from typing import Optional

from .request import Request
from .response_description import (
    ResponseDescription,
    ResponseVerification,
)
from .status import Status, merge_statuses
from .verification import Verification


@dataclass(frozen=True)
class CaseResult:
    status: Status
    request: Verification
    response: Optional[ResponseVerification] = None
    label: Optional[str] = None


class Case:

    def __init__(
        self,
        request: Request,
        response_description: ResponseDescription,
        label: Optional[str] = None,
    ):
        self._label = label
        self._request = request
        self._response_description = response_description

    def __call__(self, base_url: str, retry: int = 0) -> CaseResult:
        if retry < 0:
            raise ValueError(
                f'Retry count must be positive or 0, given {retry}'
            )
        for _ in range(1 + retry):
            result = self._run(base_url)
            if result.status.is_succeeded:
                break

        return result

    def _run(self, base_url: str) -> CaseResult:
        try:
            response = self._request(base_url)
        except Exception as error:
            return CaseResult(
                status=Status.FAILURE,
                request=Verification.of_error(error),
            )
        request_verification = Verification.succeed()

        response_verification = self._response_description.verify(
            status_code=response.status_code,
            headers=response.headers,
            body=response.body,
            request_datetime=response.request_datetime,
        )

        status = merge_statuses(
            request_verification.status,
            response_verification.status,
        )
        return CaseResult(
            status=status,
            request=request_verification,
            response=response_verification,
            label=self._label,
        )

    @property
    def label(self) -> Optional[str]:
        return self._label

    @property
    def request(self) -> Request:
        return self._request

    @property
    def response_description(self) -> ResponseDescription:
        return self._response_description
