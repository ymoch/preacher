from concurrent.futures import Executor
from typing import Iterable, Optional, Iterator

from preacher.core.status import Status
from .case_runner import CaseRunner
from .listener import Listener
from .scenario import Scenario, ScenarioResult, ScenarioTask, StaticScenarioTask


class ScenarioRunner:

    def __init__(self, case_runner: CaseRunner):
        self._case_runner = case_runner

    def run(
        self,
        executor: Executor,
        scenarios: Iterable[Scenario],
        listener: Optional[Listener] = None,
    ) -> Status:
        """
        Run the scenarios.

        Args:
            executor: An executor to submit scenarios.
            scenarios: An iterator of scenarios,
                which can raise `Exception` for each iteration.
            listener: A listener for each scenario running.
        Returns:
            The execution status.
        """
        listener = listener or Listener()

        tasks = self._submit_all(executor, scenarios, listener)
        results = (task.result() for task in list(tasks))

        status = Status.SKIPPED
        for result in results:
            status = status.merge(result.status)
            listener.on_scenario(result)

        listener.on_end(status)
        return status

    def _submit_all(
        self,
        executor: Executor,
        scenarios: Iterable[Scenario],
        listener: Optional[Listener] = None,
    ) -> Iterator[ScenarioTask]:
        iterator = iter(scenarios)
        while True:
            try:
                scenario = next(iterator)
            except StopIteration:
                break
            except Exception as error:
                result = ScenarioResult(
                    label='Not a constructed scenario',
                    status=Status.FAILURE,
                    message=f'{error.__class__.__name__}: {error}',
                )
                yield StaticScenarioTask(result)
                continue

            yield scenario.submit(executor, self._case_runner, listener)
