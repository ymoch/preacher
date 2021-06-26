from abc import ABC, abstractmethod
from typing import Optional, List

from preacher.core.status import StatusedList, merge_statuses
from preacher.core.verification import Verification
from .scenario_result import ScenarioResult
from .util.concurrency import CasesTask


class ScenarioTask(ABC):
    @abstractmethod
    def result(self) -> ScenarioResult:
        ...  # pragma: no cover


class StaticScenarioTask(ScenarioTask):
    def __init__(self, result: ScenarioResult):
        self._result = result

    def result(self) -> ScenarioResult:
        return self._result


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
        subscenarios = StatusedList.collect(s.result() for s in self._subscenarios)
        return ScenarioResult(
            label=self._label,
            status=merge_statuses([cases.status, subscenarios.status]),
            conditions=self._conditions,
            cases=cases,
            subscenarios=subscenarios,
        )
