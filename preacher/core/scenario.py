"""Scenario"""

from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import List, Optional

from .case import Case, CaseResult
from .status import Status, merge_statuses


@dataclass(frozen=True)
class ScenarioResult:
    label: Optional[str]
    status: Status
    message: Optional[str] = None
    cases: List[CaseResult] = field(default_factory=list)


class ScenarioTask:

    def __init__(self, label: Optional[str], cases_future: Future):
        self._label = label
        self._cases_future = cases_future

    def result(self) -> ScenarioResult:
        cases = self._cases_future.result()
        status = merge_statuses(result.status for result in cases)
        return ScenarioResult(
            label=self._label,
            status=status,
            cases=cases,
        )


class Scenario:

    def __init__(
        self,
        label: Optional[str] = None,
        cases: List[Case] = [],
    ):
        self._label = label
        self._cases = cases

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
        cases_future = executor.submit(
            self._run_cases,
            base_url=base_url,
            retry=retry,
            delay=delay,
            timeout=timeout,
        )
        return ScenarioTask(label=self._label, cases_future=cases_future)

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
