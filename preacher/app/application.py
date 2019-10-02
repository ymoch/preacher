from concurrent.futures import Executor
from typing import Callable, Iterable, List, Optional

import ruamel.yaml as yaml

from preacher.core.scenario import ScenarioResult
from preacher.core.status import Status
from preacher.compilation.error import CompilationError
from preacher.compilation.scenario import ScenarioCompiler
from .listener import Listener


class Application:
    def __init__(
        self,
        presentations: List[Listener],
        base_url: str,
        retry: int = 0,
        delay: float = 0.1,
        timeout: Optional[float] = None,
    ):
        self._presentations = presentations
        self._base_url = base_url
        self._retry = retry
        self._delay = delay
        self._timeout = timeout

        self._scenario_compiler = ScenarioCompiler()
        self._is_succeeded = True

    @property
    def is_succeeded(self) -> bool:
        return self._is_succeeded

    def run(self, executor: Executor, config_paths: Iterable[str]) -> None:
        tasks = [self._submit_each(executor, path) for path in config_paths]
        results = (task() for task in tasks)
        for result in results:
            self._is_succeeded &= result.status.is_succeeded
            for presentation in self._presentations:
                presentation.accept(result)

    def _submit_each(
        self,
        executor: Executor,
        config_path: str,
    ) -> Callable[[], ScenarioResult]:
        with open(config_path) as config_file:
            config = yaml.safe_load(config_file)

        try:
            scenario = self._scenario_compiler.compile(config)
        except CompilationError as error:
            result = ScenarioResult(
                label=f'Compilation Error ({config_path})',
                status=Status.FAILURE,
                message=str(error),
            )
            return lambda: result

        return scenario.submit(
            executor,
            base_url=self._base_url,
            retry=self._retry,
            delay=self._delay,
            timeout=self._timeout,
        ).result