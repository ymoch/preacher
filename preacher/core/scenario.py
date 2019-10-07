"""Scenario"""

from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import (
    Any, Iterable, Iterator, List, Optional, Sequence, TypeVar, Union
)

from .case import Case, CaseResult
from .context import Context
from .description import Description
from .status import Status, merge_statuses
from .verification import Verification


T = TypeVar('T')


class VerificationSequence(Sequence[T]):

    def __init__(
        self, status: Status = Status.SKIPPED,
        items: Sequence[T] = [],
    ):
        self._status = status
        self._items = items

    @property
    def status(self) -> Status:
        return self._status

    def __contains__(self, item: Any) -> bool:
        return item in self._items

    def __bool__(self) -> bool:
        return bool(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[T]:
        return iter(self._items)

    def __getitem__(self, key):
        return self._items[key]

    def __reversed__(self):
        return VerificationSequence(
            status=self._status,
            items=list(reversed(self._items)),
        )


@dataclass(frozen=True)
class ScenarioResult:
    label: Optional[str]
    status: Status
    message: Optional[str] = None
    conditions: VerificationSequence[Verification] = field(
        default_factory=VerificationSequence,
    )
    cases: VerificationSequence[CaseResult] = field(
        default_factory=VerificationSequence,
    )
    subscenarios: VerificationSequence[ScenarioResult] = field(
        default_factory=VerificationSequence,
    )


Statused = TypeVar('Statused', Verification, CaseResult, ScenarioResult)


def collect(items: Iterable[Statused]) -> VerificationSequence[Statused]:
    items = list(items)
    status = merge_statuses(item.status for item in items)
    return VerificationSequence(status=status, items=items)


class RunningScenarioTask:

    def __init__(
        self, label: Optional[str],
        conditions: VerificationSequence[Verification],
        cases: Future,
        subscenarios: List[ScenarioTask],
    ):
        self._label = label
        self._conditions = conditions
        self._cases = cases
        self._subscenarios = subscenarios

    def result(self) -> ScenarioResult:
        cases = self._cases.result()
        subscenarios = collect(s.result() for s in self._subscenarios)
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
            condition(context_analyzer)
            for condition in self._conditions
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
    ) -> VerificationSequence[CaseResult]:
        return collect(
            case(base_url, timeout=timeout, retry=retry, delay=delay)
            for case in self._cases
        )
