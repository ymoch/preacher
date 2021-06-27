from concurrent.futures import Executor
from typing import Iterable, Iterator, Optional

from preacher.core.scenario import CaseRunner
from preacher.core.scenario import Scenario
from preacher.core.scenario import ScenarioRunner
from preacher.core.scenario import ScenarioResult
from preacher.core.scenario import ScenarioTask
from preacher.core.scenario.scenario_task import StaticScenarioTask
from preacher.core.status import Status
from preacher.core.request import Requester
from preacher.core.unit import UnitRunner
from .listener import Listener


class ScenarioScheduler:
    def __init__(self, runner: ScenarioRunner, listener: Optional[Listener] = None):
        self._runner = runner
        self._listener = listener or Listener()

    def run(self, scenarios: Iterable[Scenario]) -> Status:
        """
        Run the scenarios.

        Args:
            scenarios: An iterator of scenarios,
                which can raise `Exception` for each iteration.
        Returns:
            The execution status.
        """
        tasks = self._submit_all(scenarios)
        results = (task.result() for task in list(tasks))

        status = Status.SKIPPED
        for result in results:
            status = status.merge(result.status)
            self._listener.on_scenario(result)

        self._listener.on_end(status)
        return status

    def _submit_all(self, scenarios: Iterable[Scenario]) -> Iterator[ScenarioTask]:
        iterator = iter(scenarios)
        while True:
            try:
                scenario = next(iterator)
            except StopIteration:
                break
            except Exception as error:
                result = ScenarioResult(
                    label="Not a constructed scenario",
                    status=Status.FAILURE,
                    message=f"{error.__class__.__name__}: {error}",
                )
                yield StaticScenarioTask(result)
                continue

            yield self._runner.submit(scenario)


def create_scheduler(
    executor: Executor,
    listener: Listener,
    base_url: str,
    timeout: Optional[float],
    retry: int,
    delay: float,
) -> ScenarioScheduler:
    requester = Requester(base_url=base_url, timeout=timeout)
    unit_runner = UnitRunner(requester=requester, retry=retry, delay=delay)
    case_runner = CaseRunner(unit_runner=unit_runner, listener=listener)
    runner = ScenarioRunner(executor=executor, case_runner=case_runner)
    return ScenarioScheduler(runner=runner, listener=listener)
