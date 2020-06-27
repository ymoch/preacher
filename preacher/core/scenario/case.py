"""
Test cases, which execute a given request and verify its response
along the given descriptions.
"""
from dataclasses import dataclass, field, replace
from datetime import datetime
from functools import partial
from typing import Optional, List

from requests import Session

from preacher.core.datetime import now
from preacher.core.response import Response
from .analysis import analyze_data_obj
from .description import Description
from .request import Request
from .response import ResponseDescription, ResponseVerification
from .status import Status, Statused, merge_statuses
from .util.retry import retry_while_false
from .verification import Verification, collect


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
    label: Optional[str] = None
    conditions: Verification = field(default_factory=Verification)
    request: Request = field(default_factory=Request)
    execution: Verification = field(default_factory=Verification)
    response: Optional[ResponseVerification] = None

    @property
    def status(self) -> Status:  # HACK: should be cached
        if self.conditions.status == Status.UNSTABLE:
            return Status.SKIPPED
        if self.conditions.status == Status.FAILURE:
            return Status.FAILURE

        return merge_statuses([
            self.execution.status,
            self.response.status if self.response else Status.SKIPPED,
        ])


@dataclass(frozen=True)
class CaseContext:
    starts: datetime = field(default_factory=now)
    base_url: str = ''
    retry: int = 0
    delay: float = 0.1
    timeout: Optional[float] = None


class Case:
    """
    Test cases, which execute a given request and verify its response
    along the given descriptions.
    """

    def __init__(
        self,
        label: Optional[str] = None,
        enabled: bool = True,
        conditions: Optional[List[Description]] = None,
        request: Optional[Request] = None,
        response: Optional[ResponseDescription] = None,
    ):
        self._label = label
        self._enabled = enabled
        self._conditions = conditions or []
        self._request = request or Request()
        self._response = response or ResponseDescription()

    def run(
        self,
        base_url: str = '',
        retry: int = 0,
        delay: float = 0.1,
        timeout: Optional[float] = None,
        listener: Optional[CaseListener] = None,
        session: Optional[Session] = None,
    ) -> CaseResult:
        if not self._enabled:
            return CaseResult(label=self._label)

        context = CaseContext(
            base_url=base_url,
            retry=retry,
            delay=delay,
            timeout=timeout,
        )
        context_analyzer = analyze_data_obj(context)
        conditions = collect(
            condition.verify(context_analyzer, origin_datetime=context.starts)
            for condition in self._conditions
        )
        if not conditions.status.is_succeeded:
            return CaseResult(label=self._label, conditions=conditions)

        listener = listener or CaseListener()
        func = partial(self._run, base_url, timeout, listener, session)
        result = retry_while_false(func, attempts=retry + 1, delay=delay)
        return replace(result, conditions=conditions)

    def _run(
        self,
        base_url: str,
        timeout: Optional[float],
        listener: CaseListener,
        session: Optional[Session],
    ) -> CaseResult:
        try:
            response = self._request(
                base_url,
                timeout=timeout,
                session=session,
            )
        except Exception as error:
            return CaseResult(
                label=self._label,
                request=self._request,
                execution=Verification.of_error(error),
            )
        listener.on_response(response)

        execution_verification = Verification.succeed()
        response_verification = self._response.verify(
            response,
            origin_datetime=response.starts,
        )
        return CaseResult(
            label=self._label,
            request=self._request,
            execution=execution_verification,
            response=response_verification,
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
