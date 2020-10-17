from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import requests

from preacher.core.datetime import now
from preacher.core.extraction import analyze_data_obj
from preacher.core.request import ExecutionReport, Response
from preacher.core.status import Statused, Status, merge_statuses
from preacher.core.unit import UnitRunner
from preacher.core.value import ValueContext
from preacher.core.verification import Verification, ResponseVerification
from .case import Case


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


class CaseRunner:

    def __init__(self, unit_runner: UnitRunner):
        self._unit_runner = unit_runner

    @property
    def base_url(self) -> str:
        return self._unit_runner.base_url

    def run(
        self,
        case: Case,
        listener: Optional[CaseListener] = None,
        session: Optional[requests.Session] = None,
    ) -> CaseResult:
        if not case.enabled:
            return CaseResult(label=case.label)

        context = CaseContext(base_url=self._unit_runner.base_url)
        context_analyzer = analyze_data_obj(context)
        value_context = ValueContext(origin_datetime=context.starts)
        conditions = Verification.collect(
            condition.verify(context_analyzer, value_context)
            for condition in case.conditions
        )
        if not conditions.status.is_succeeded:
            return CaseResult(case.label, conditions)

        execution, response, verification = self._unit_runner.run(
            request=case.request,
            requirements=case.response,
            session=session,
        )
        if listener:
            listener.on_execution(execution, response)

        return CaseResult(case.label, conditions, execution, verification)
