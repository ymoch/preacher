from concurrent.futures import ThreadPoolExecutor
from typing import Iterable, Optional

from preacher.core.scenario import Scenario
from preacher.listener import Listener


class ScenarioRunner:
    def __init__(
        self,
        base_url: str,
        retry: int = 0,
        delay: float = 0.1,
        timeout: Optional[float] = None,
        listener: Optional[Listener] = None,
    ):
        self._base_url = base_url
        self._retry = retry
        self._delay = delay
        self._timeout = timeout
        self._listener = listener or Listener()

        self._is_succeeded = True

    @property
    def is_succeeded(self) -> bool:
        return self._is_succeeded

    def run(
        self,
        executor: ThreadPoolExecutor,
        scenarios: Iterable[Scenario],
    ) -> None:
        tasks = [
            scenario.submit(
                executor,
                base_url=self._base_url,
                retry=self._retry,
                delay=self._delay,
                timeout=self._timeout,
                listener=self._listener,
            )
            for scenario in scenarios
        ]
        results = (task.result() for task in tasks)
        for result in results:
            self._is_succeeded &= result.status.is_succeeded
            self._listener.on_scenario(result)

        self._listener.on_end()
