"""Scenario"""

from __future__ import annotations

from concurrent.futures import Executor
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, List, Optional

from preacher.core.datetime import now
from preacher.core.extraction import analyze_data_obj
from preacher.core.status import Status
from preacher.core.value import ValueContext
from preacher.core.verification import Description, Verification
from .case import Case
from .case_runner import CaseRunner, CaseListener
from .scenario_result import ScenarioResult
from .scenario_task import RunningScenarioTask, StaticScenarioTask
from .scenario_task import ScenarioTask
from .util.concurrency import OrderedCasesTask, UnorderedCasesTask


class ScenarioListener(CaseListener):
    """
    Interface to listen to scenario running.
    """
    pass


@dataclass(frozen=True)
class ScenarioContext:
    starts: datetime = field(default_factory=now)
    base_url: str = ''


class Scenario:

    def __init__(
        self,
        label: Optional[str] = None,
        ordered: bool = True,
        conditions: Optional[List[Description]] = None,
        cases: Optional[List[Case]] = None,
        subscenarios: Optional[List[Scenario]] = None,
    ):
        self._label = label
        self._ordered = ordered
        self._conditions = conditions or []
        self._cases = cases or []
        self._subscenarios = subscenarios or []

    @property
    def label(self) -> Optional[str]:
        return self._label

    def submit(
        self,
        executor: Executor,
        case_runner: CaseRunner,
        listener: Optional[ScenarioListener] = None,
    ) -> ScenarioTask:
        context = ScenarioContext(base_url=case_runner.base_url)
        context_analyzer = analyze_data_obj(context)
        value_context = ValueContext(origin_datetime=context.starts)
        conditions = Verification.collect(
            condition.verify(context_analyzer, value_context)
            for condition in self._conditions
        )
        if not conditions.status.is_succeeded:
            status = Status.SKIPPED
            if conditions.status is Status.FAILURE:
                status = Status.FAILURE

            result = ScenarioResult(
                label=self._label,
                status=status,
                conditions=conditions,
            )
            return StaticScenarioTask(result)

        listener = listener or ScenarioListener()

        if self._ordered:
            submit_cases: Callable = OrderedCasesTask
        else:
            submit_cases = UnorderedCasesTask
        cases = submit_cases(executor, case_runner, self._cases, listener)

        subscenarios = [
            subscenario.submit(executor, case_runner, listener)
            for subscenario in self._subscenarios
        ]
        return RunningScenarioTask(
            label=self._label,
            conditions=conditions,
            cases=cases,
            subscenarios=subscenarios,
        )
