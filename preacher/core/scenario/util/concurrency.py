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


def _run_cases_in_order(
    case_runner: CaseRunner,
    cases: Iterable[Case],
    *args,
    **kwargs,
) -> StatusedList[CaseResult]:
    if not kwargs.get("session"):
        with Session() as session:
            kwargs["session"] = session
            return _run_cases_in_order(case_runner, cases, *args, **kwargs)

    return StatusedList.collect(case_runner.run(case, *args, **kwargs) for case in cases)


class OrderedCasesTask(CasesTask):
    def __init__(
        self,
        executor: Executor,
        case_runner: CaseRunner,
        cases: Iterable[Case],
        *args,
        **kwargs,
    ):
        self._future = executor.submit(
            _run_cases_in_order,
            case_runner,
            cases,
            *args,
            **kwargs,
        )

    def result(self) -> StatusedList[CaseResult]:
        return self._future.result()


class UnorderedCasesTask(CasesTask):
    def __init__(
        self,
        executor: Executor,
        case_runner: CaseRunner,
        cases: Iterable[Case],
        *args,
        **kwargs,
    ):
        self._futures = [executor.submit(case_runner.run, case, *args, **kwargs) for case in cases]

    def result(self) -> StatusedList[CaseResult]:
        return StatusedList.collect(f.result() for f in self._futures)
