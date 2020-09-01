"""
Test cases, which execute a given request and verify its response
along the given descriptions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

from requests import Session

from preacher.core.datetime import now
from preacher.core.executor import Executor
from preacher.core.extraction import analyze_data_obj
from preacher.core.request import Request, Response, ExecutionReport
from preacher.core.status import Status, Statused, merge_statuses
from preacher.core.value import ValueContext
from preacher.core.verification import Description
from preacher.core.verification import ResponseDescription
from preacher.core.verification import ResponseVerification
from preacher.core.verification import Verification


class CaseListener:
    """
    Interface to listen to running cases.
    Default implementations do nothing.
    """

    def on_execution(self, execution: ExecutionReport, response: Optional[Response]) -> None:
        pass


@dataclass(frozen=True)
class CaseResult(Statused):
    """
    Results for the test cases.
    """
    label: Optional[str] = None
    conditions: Verification = field(default_factory=Verification)
    execution: ExecutionReport = field(default_factory=ExecutionReport)
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
        listener = listener or CaseListener()

        if not self._enabled:
            return CaseResult(label=self._label)

        context = CaseContext(
            base_url=base_url,
            retry=retry,
            delay=delay,
            timeout=timeout,
        )
        context_analyzer = analyze_data_obj(context)
        value_context = ValueContext(origin_datetime=context.starts)
        conditions = Verification.collect(
            condition.verify(context_analyzer, value_context)
            for condition in self._conditions
        )
        if not conditions.status.is_succeeded:
            return CaseResult(self._label, conditions)

        executor = Executor(
            base_url=base_url,
            retry=retry,
            delay=delay,
            timeout=timeout,
            session=session,
        )

        execution, response, verification = executor.execute(self.request, self.response)
        listener.on_execution(execution, response)
        return CaseResult(self._label, conditions, execution, verification)

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
