"""
Test cases, which execute a given request and verify its response
along the given descriptions.
"""

from dataclasses import dataclass, field
from functools import partial
from typing import Optional

from preacher.core.response import Response
from .request import Request
from .response_description import ResponseDescription, ResponseVerification
from .status import Status, Statused, merge_statuses
from .util.retry import retry_while_false
from .verification import Verification


class CaseListener:
    """
    Interface to listen to running cases.
    Default implementations do nothing.
    """

    def on_response(self, response: Response) -> None:
        pass


@dataclass(frozen=True)
class RequestReport:
    request: Request = field(default_factory=Request)
    result: Verification = field(default_factory=Verification)


@dataclass(frozen=True)
class CaseResult(Statused):
    """
    Results for the test cases.
    """
    request: Request = field(default_factory=Request)
    execution: Verification = field(default_factory=Verification)
    response: Optional[ResponseVerification] = None
    label: Optional[str] = None

    @property
    def status(self) -> Status:  # HACK: should be cached
        return merge_statuses([
            self.execution.status,
            self.response.status if self.response else Status.SKIPPED,
        ])


class Case:
    """
    Test cases, which execute a given request and verify its response
    along the given descriptions.
    """

    def __init__(
        self,
        label: Optional[str] = None,
        enabled: bool = True,
        request: Optional[Request] = None,
        response: Optional[ResponseDescription] = None,
    ):
        self._label = label
        self._enabled = enabled
        self._request = request or Request()
        self._response = response or ResponseDescription()

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
                request=self._request,
                execution=Verification.of_error(error),
                label=self._label,
            )
        listener.on_response(response)

        execution_verification = Verification.succeed()
        response_verification = self._response.verify(
            response,
            origin_datetime=response.starts,
        )
        return CaseResult(
            request=self._request,
            execution=execution_verification,
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
    def response(self) -> ResponseDescription:
        return self._response
