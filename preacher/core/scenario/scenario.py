"""Scenario"""

from __future__ import annotations

from abc import ABC, abstractmethod
from concurrent.futures import Executor, ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Iterator

from .case import Case, CaseListener, CaseResult
from .context import ScenarioContext, analyze_context
from .description import Description
from .status import (
    Status, StatusedMixin, StatusedSequence, collect_statused, merge_statuses
)
from .util.concurrency import CasesTask, OrderedCasesTask, UnorderedCasesTask
from .verification import Verification, collect


class ScenarioListener(CaseListener):
    """
    Interface to listen to scenario running.
    """
    pass


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


def _run_cases_in_order(
    cases: Iterable[Case],
    *args,
    **kwargs
) -> Iterator[CaseResult]:
    return (case.run(*args, **kwargs) for case in cases)


def _submit_ordered_cases(
    executor: Executor,
    cases: Iterable[Case],
    base_url: str,
    retry: int,
    delay: float,
    timeout: Optional[float],
    listener: Optional[CaseListener],
) -> CasesTask:
    return OrderedCasesTask(
        executor,
        cases,
        base_url=base_url,
        retry=retry,
        delay=delay,
        timeout=timeout,
        listener=listener,
    )


def _submit_unordered_cases(
    executor: Executor,
    cases: Iterable[Case],
    base_url: str,
    retry: int,
    delay: float,
    timeout: Optional[float],
    listener: Optional[CaseListener],
) -> CasesTask:
    return UnorderedCasesTask(
        executor,
        cases,
        base_url=base_url,
        retry=retry,
        delay=delay,
        timeout=timeout,
        listener=listener,
    )


class ScenarioTask(ABC):

    @abstractmethod
    def result(self) -> ScenarioResult:
        raise NotImplementedError()


class RunningScenarioTask(ScenarioTask):

    def __init__(
        self,
        label: Optional[str],
        conditions: Verification,
        cases: CasesTask,
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


class StaticScenarioTask(ScenarioTask):

    def __init__(self, result: ScenarioResult):
        self._result = result

    def result(self) -> ScenarioResult:
        return self._result


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

    def run(
        self,
        base_url: str = '',
        retry: int = 0,
        delay: float = 0.1,
        timeout: Optional[float] = None,
        listener: Optional[ScenarioListener] = None,
    ) -> ScenarioResult:
        with ThreadPoolExecutor(1) as executor:
            return self.submit(
                executor,
                base_url=base_url,
                retry=retry,
                delay=delay,
                timeout=timeout,
                listener=listener,
            ).result()

    def submit(
        self,
        executor: Executor,
        base_url: str = '',
        retry: int = 0,
        delay: float = 0.1,
        timeout: Optional[float] = None,
        listener: Optional[ScenarioListener] = None,
    ) -> ScenarioTask:
        context = ScenarioContext(
            base_url=base_url,
            retry=retry,
            delay=delay,
            timeout=timeout,
        )
        context_analyzer = analyze_context(context)
        conditions = collect(
            condition.verify(context_analyzer, origin_datetime=context.starts)
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

        listener = listener or ScenarioListener()

        if self._ordered:
            submit_cases = _submit_ordered_cases
        else:
            submit_cases = _submit_unordered_cases
        cases = submit_cases(
            executor,
            self._cases,
            base_url=base_url,
            retry=retry,
            delay=delay,
            timeout=timeout,
            listener=listener,
        )

        subscenarios = [
            subscenario.submit(
                executor,
                base_url=base_url,
                retry=retry,
                delay=delay,
                timeout=timeout,
                listener=listener,
            )
            for subscenario in self._subscenarios
        ]
        return RunningScenarioTask(
            label=self._label,
            conditions=conditions,
            cases=cases,
            subscenarios=subscenarios,
        )
