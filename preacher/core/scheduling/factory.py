from concurrent.futures import Executor
from typing import Optional

from preacher.core.request import Requester
from preacher.core.scenario import CaseRunner, ScenarioRunner
from preacher.core.unit import UnitRunner
from .listener import Listener
from .scenario_scheduler import ScenarioScheduler


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
