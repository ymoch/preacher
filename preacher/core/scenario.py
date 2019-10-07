"""Scenario"""

from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from itertools import chain
from typing import List, Optional

from .case import Case, CaseResult
from .status import Status, merge_statuses


@dataclass(frozen=True)
class ScenarioResult:
    label: Optional[str]
    status: Status
    message: Optional[str] = None
    cases: List[CaseResult] = field(default_factory=list)
    subscenarios: List[ScenarioResult] = field(default_factory=list)


class ScenarioTask:

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


class Scenario:

    def __init__(
        self,
        label: Optional[str] = None,
        cases: List[Case] = [],
        subscenarios: List[Scenario] = [],
    ):
        self._label = label
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
        return ScenarioTask(
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
