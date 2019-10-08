"""Scenario"""

from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import List, Optional, Union

from .case import Case, CaseResult
from .context import Context
from .description import Description
from .status import (
    Status, StatusedMixin, StatusedSequence, collect_statused, merge_statuses
)
from .verification import Verification, collect


@dataclass(frozen=True)
class ScenarioResult(StatusedMixin):
    label: Optional[str] = None
    message: Optional[str] = None
    conditions: Verification = field(default_factory=Verification)
    cases: StatusedSequence[CaseResult] = field(
        default_factory=StatusedSequence,
    )
    subscenarios: StatusedSequence[ScenarioResult] = field(
        default_factory=StatusedSequence,
    )


class RunningScenarioTask:

    def __init__(
        self, label: Optional[str],
        conditions: Verification,
        cases: Future,
        subscenarios: List[ScenarioTask],
    ):
        self._label = label
        self._conditions = conditions
        self._cases = cases
        self._subscenarios = subscenarios

    def result(self) -> ScenarioResult:
        cases = self._cases.result()
        subscenarios = collect_statused(s.result() for s in self._subscenarios)
        status = merge_statuses(cases.status, subscenarios.status)
        return ScenarioResult(
            label=self._label,
            status=status,
            conditions=self._conditions,
            cases=cases,
            subscenarios=subscenarios,
        )


class StaticScenarioTask:

    def __init__(self, result: ScenarioResult):
        self._result = result

    def result(self) -> ScenarioResult:
        return self._result


ScenarioTask = Union[RunningScenarioTask, StaticScenarioTask]


class Scenario:

    def __init__(
        self,
        label: Optional[str] = None,
        conditions: List[Description] = [],
        cases: List[Case] = [],
        subscenarios: List[Scenario] = [],
    ):
        self._label = label
        self._conditions = conditions
        self._cases = cases
        self._subscenarios = subscenarios

    def run(
        self,
        base_url: str,
        retry: int = 0,
        delay: float = 0.1,
        timeout: Optional[float] = None,
    ) -> ScenarioResult:
        with ThreadPoolExecutor(1) as executor:
            return self.submit(
                executor,
                base_url=base_url,
                retry=retry,
                delay=delay,
                timeout=timeout,
            ).result()

    def submit(
        self,
        executor: ThreadPoolExecutor,
        base_url: str,
        retry: int = 0,
        delay: float = 0.1,
        timeout: Optional[float] = None,
    ) -> ScenarioTask:
        context = Context(base_url=base_url)
        context_analyzer = context.analyze()
        conditions = collect(
            condition(context_analyzer) for condition in self._conditions
        )
        if conditions.status == Status.FAILURE:
            return StaticScenarioTask(ScenarioResult(
                label=self._label,
                status=Status.FAILURE,
                conditions=conditions,
            ))
        if conditions.status == Status.UNSTABLE:
            return StaticScenarioTask(ScenarioResult(
                label=self._label,
                status=Status.SKIPPED,
                conditions=conditions,
            ))

        cases = executor.submit(
            self._run_cases,
            base_url=base_url,
            retry=retry,
            delay=delay,
            timeout=timeout,
        )
        subscenarios = [
            subscenario.submit(
                executor,
                base_url=base_url,
                retry=retry,
                delay=delay,
                timeout=timeout,
            )
            for subscenario in self._subscenarios
        ]
        return RunningScenarioTask(
            label=self._label,
            conditions=conditions,
            cases=cases,
            subscenarios=subscenarios,
        )

    def _run_cases(
        self,
        base_url: str,
        retry: int = 0,
        delay: float = 0.1,
        timeout: Optional[float] = None,
    ) -> StatusedSequence[CaseResult]:
        return collect_statused(
            case(base_url, timeout=timeout, retry=retry, delay=delay)
            for case in self._cases
        )
