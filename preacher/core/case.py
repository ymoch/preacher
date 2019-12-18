"""Test case."""

from dataclasses import dataclass, field
from functools import partial
from typing import Optional

from .internal.retry import retry_while_false
from .request import Request, Response
from .response_description import (
    ResponseDescription,
    ResponseVerification,
)
from .status import Status, StatusedMixin, merge_statuses
from .verification import Verification


class CaseListener:
    """
    Interface to listen to running cases.
    Default implementations do nothing.
    """

    def on_response(self, response: Response) -> None:
        pass


@dataclass(frozen=True)
class CaseResult(StatusedMixin):
    request: Verification = field(default_factory=Verification)
    response: Optional[ResponseVerification] = None
    label: Optional[str] = None

    def __bool__(self) -> bool:
        return bool(self.status)


class Case:

    def __init__(
        self,
        request: Request,
        response_description: ResponseDescription,
        label: Optional[str] = None,
        enabled: bool = True,
    ):
        self._label = label
        self._request = request
        self._response_description = response_description
        self._enabled = enabled

    def run(
        self,
        base_url: str = '',
        retry: int = 0,
        delay: float = 0.1,
        timeout: Optional[float] = None,
        listener: Optional[CaseListener] = None,
    ) -> CaseResult:
        if not self._enabled:
            return CaseResult(label=self._label)
        listener = listener or CaseListener()
        func = partial(self._run, base_url, timeout, listener)
        return retry_while_false(func, attempts=retry + 1, delay=delay)

    def _run(
        self,
        base_url: str,
        timeout: Optional[float],
        listener: CaseListener,
    ) -> CaseResult:
        try:
            response = self._request(base_url, timeout=timeout)
        except Exception as error:
            return CaseResult(
                status=Status.FAILURE,
                request=Verification.of_error(error),
                label=self._label,
            )
        listener.on_response(response)

        request_verification = Verification.succeed()
        response_verification = self._response_description.verify(
            response,
            origin_datetime=response.request_datetime,
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
    def enabled(self) -> bool:
        return self._enabled

    @property
    def request(self) -> Request:
        return self._request

    @property
    def response_description(self) -> ResponseDescription:
        return self._response_description
