from concurrent.futures import Executor
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable

from preacher.core.datetime import now
from preacher.core.extraction import analyze_data_obj
from preacher.core.status import Status
from preacher.core.value import ValueContext
from preacher.core.verification import Verification
from .case_runner import CaseRunner
from .scenario import Scenario
from .scenario_result import ScenarioResult
from .scenario_task import ScenarioTask, StaticScenarioTask, RunningScenarioTask
from .util.concurrency import OrderedCasesTask, UnorderedCasesTask


@dataclass(frozen=True)
class ScenarioContext:
    starts: datetime = field(default_factory=now)
    base_url: str = ""


class ScenarioRunner:
    def __init__(self, executor: Executor, case_runner: CaseRunner):
        self._executor = executor
        self._case_runner = case_runner

    def submit(self, scenario: Scenario) -> ScenarioTask:
        context = ScenarioContext(base_url=self._case_runner.base_url)
        context_analyzer = analyze_data_obj(context)
        value_context = ValueContext(origin_datetime=context.starts)
        conditions = Verification.collect(
            condition.verify(context_analyzer, value_context) for condition in scenario.conditions
        )
        if not conditions.status.is_succeeded:
            status = Status.SKIPPED
            if conditions.status is Status.FAILURE:
                status = Status.FAILURE

            result = ScenarioResult(label=scenario.label, status=status, conditions=conditions)
            return StaticScenarioTask(result)

        if scenario.ordered:
            submit_cases: Callable = OrderedCasesTask
        else:
            submit_cases = UnorderedCasesTask
        cases = submit_cases(self._executor, self._case_runner, scenario.cases)
        subscenarios = [self.submit(subscenario) for subscenario in scenario.subscenarios]
        return RunningScenarioTask(
            label=scenario.label,
            conditions=conditions,
            cases=cases,
            subscenarios=subscenarios,
        )
