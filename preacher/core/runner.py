from concurrent.futures import ThreadPoolExecutor
from typing import Iterable, Optional

from .listener import Listener
from .scenario import Scenario
from .scenario.status import Status


class ScenarioRunner:

    def __init__(
        self,
        base_url: str = '',
        retry: int = 0,
        delay: float = 0.1,
        timeout: Optional[float] = None,
    ):
        self._base_url = base_url
        self._retry = retry
        self._delay = delay
        self._timeout = timeout

    def run(
        self,
        executor: ThreadPoolExecutor,
        scenarios: Iterable[Scenario],
        listener: Optional[Listener] = None,
    ) -> Status:
        listener = listener or Listener()
        tasks = [
            scenario.submit(
                executor,
                base_url=self._base_url,
                retry=self._retry,
                delay=self._delay,
                timeout=self._timeout,
                listener=listener,
            )
            for scenario in scenarios
        ]
        results = (task.result() for task in tasks)

        status = Status.SKIPPED
        for result in results:
            status = status.merge(result.status)
            listener.on_scenario(result)

        listener.on_end()
        return status
