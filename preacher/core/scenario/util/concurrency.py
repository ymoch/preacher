from abc import ABC, abstractmethod
from concurrent.futures import Executor
from typing import Iterable

from preacher.core.scenario.case import Case, CaseResult
from preacher.core.scenario.status import StatusedSequence, collect_statused


class CasesTask(ABC):

    @abstractmethod
    def result(self) -> StatusedSequence[CaseResult]:
        raise NotImplementedError()


def _run_cases_in_order(
    cases: Iterable[Case],
    *args,
    **kwargs
) -> StatusedSequence[CaseResult]:
    return collect_statused(case.run(*args, **kwargs) for case in cases)


class OrderedCasesTask(CasesTask):

    def __init__(
        self,
        executor: Executor,
        cases: Iterable[Case],
        *args,
        **kwargs,
    ):
        self._future = executor.submit(
            _run_cases_in_order,
            cases,
            *args,
            **kwargs,
        )

    def result(self) -> StatusedSequence[CaseResult]:
        return self._future.result()


class UnorderedCasesTask(CasesTask):

    def __init__(
        self,
        executor: Executor,
        cases: Iterable[Case],
        *args,
        **kwargs,
    ):
        self._futures = [
            executor.submit(case.run, *args, **kwargs)
            for case in cases
        ]

    def result(self) -> StatusedSequence[CaseResult]:
        return collect_statused(f.result() for f in self._futures)
