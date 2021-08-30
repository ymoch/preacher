from abc import ABC, abstractmethod
from concurrent.futures import Executor
from typing import Iterable

from requests import Session

from preacher.core.scenario.case import Case
from preacher.core.scenario.case_result import CaseResult
from preacher.core.scenario.case_runner import CaseRunner
from preacher.core.status import StatusedList


class CasesTask(ABC):
    @abstractmethod
    def result(self) -> StatusedList[CaseResult]:
        ...  # pragma: no cover


def _run_cases_in_order(runner: CaseRunner, cases: Iterable[Case]) -> StatusedList[CaseResult]:
    with Session() as session:
        return StatusedList.collect(runner.run(case, session=session) for case in cases)


class OrderedCasesTask(CasesTask):
    def __init__(self, executor: Executor, runner: CaseRunner, cases: Iterable[Case]):
        self._future = executor.submit(_run_cases_in_order, runner, cases)

    def result(self) -> StatusedList[CaseResult]:
        return self._future.result()


class UnorderedCasesTask(CasesTask):
    def __init__(self, executor: Executor, runner: CaseRunner, cases: Iterable[Case]):
        self._futures = [executor.submit(runner.run, case) for case in cases]

    def result(self) -> StatusedList[CaseResult]:
        return StatusedList.collect(f.result() for f in self._futures)
