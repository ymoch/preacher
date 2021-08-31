from concurrent.futures import Executor

from preacher.core.context import Context, CONTEXT_KEY_BASE_URL, CONTEXT_KEY_STARTS
from preacher.core.datetime import now
from preacher.core.extraction import MappingAnalyzer
from preacher.core.status import Status
from preacher.core.verification import Verification
from .case_runner import CaseRunner
from .scenario import Scenario
from .scenario_result import ScenarioResult
from .scenario_task import ScenarioTask, StaticScenarioTask, RunningScenarioTask
from .util.concurrency import CasesTask, OrderedCasesTask, UnorderedCasesTask


class ScenarioRunner:
    def __init__(self, executor: Executor, case_runner: CaseRunner):
        self._executor = executor
        self._case_runner = case_runner

    def submit(self, scenario: Scenario) -> ScenarioTask:
        starts = now()
        context: Context = {
            CONTEXT_KEY_STARTS: starts,
            CONTEXT_KEY_BASE_URL: self._case_runner.base_url,
        }

        context_analyzer = MappingAnalyzer(context)
        conditions = Verification.collect(
            condition.verify(context_analyzer, context) for condition in scenario.conditions
        )
        if not conditions.status.is_succeeded:
            status = Status.SKIPPED
            if conditions.status is Status.FAILURE:
                status = Status.FAILURE

            result = ScenarioResult(label=scenario.label, status=status, conditions=conditions)
            return StaticScenarioTask(result)

        if scenario.ordered:
            cases: CasesTask = OrderedCasesTask(
                self._executor,
                self._case_runner,
                scenario.cases,
                context=context,
            )
        else:
            cases = UnorderedCasesTask(self._executor, self._case_runner, scenario.cases)
        subscenarios = [self.submit(subscenario) for subscenario in scenario.subscenarios]
        return RunningScenarioTask(
            label=scenario.label,
            conditions=conditions,
            cases=cases,
            subscenarios=subscenarios,
        )
