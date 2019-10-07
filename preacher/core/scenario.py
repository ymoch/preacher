"""Scenario"""

from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from itertools import chain
from typing import List, Optional, Union

from .case import Case, CaseResult
from .context import Context
from .description import Description
from .status import Status, merge_statuses


@dataclass(frozen=True)
class ScenarioResult:
    label: Optional[str]
    status: Status
    message: Optional[str] = None
    cases: List[CaseResult] = field(default_factory=list)
    subscenarios: List[ScenarioResult] = field(default_factory=list)


class RunningScenarioTask:

    def __init__(
        self, label: Optional[str],
        cases: Future,
        subscenarios: List[ScenarioTask],
    ):
        self._label = label
        self._cases = cases
        self._subscenarios = subscenarios

    def result(self) -> ScenarioResult:
        cases = self._cases.result()
        subscenarios = [s.result() for s in self._subscenarios]
        status = merge_statuses(chain(
            (case.status for case in cases),
            (subscenario.status for subscenario in subscenarios),
        ))
        return ScenarioResult(
            label=self._label,
            status=status,
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
        for cond in self._conditions:
            validation = cond(context_analyzer)
            if validation.status == Status.FAILURE:
                return StaticScenarioTask(ScenarioResult(
                    label=self._label,
                    status=Status.FAILURE,
                    message=validation.message,
                ))
            if validation.status == Status.UNSTABLE:
                return StaticScenarioTask(ScenarioResult(
                    label=self._label,
                    status=Status.SKIPPED,
                    message=validation.message,
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
            cases=cases,
            subscenarios=subscenarios,
        )

    def _run_cases(
        self,
        base_url: str,
        retry: int = 0,
        delay: float = 0.1,
        timeout: Optional[float] = None,
    ) -> List[CaseResult]:
        return [
            case(base_url, timeout=timeout, retry=retry, delay=delay)
            for case in self._cases
        ]
