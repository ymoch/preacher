from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Iterable, Optional

from preacher.compilation.argument import Arguments
from preacher.compilation.error import CompilationError
from preacher.compilation.factory import create_compiler
from preacher.compilation.yaml import load
from preacher.core.scenario import ScenarioResult
from preacher.core.scenario.status import Status
from preacher.listener import Listener


class Application:
    def __init__(
        self,
        base_url: str,
        arguments: Optional[Arguments] = None,
        retry: int = 0,
        delay: float = 0.1,
        timeout: Optional[float] = None,
        listener: Optional[Listener] = None,
    ):
        self._base_url = base_url
        self._arguments = arguments or {}
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
        config_paths: Iterable[str],
    ) -> None:
        tasks = [self._submit_each(executor, path) for path in config_paths]
        results = (task() for task in tasks)
        for result in results:
            self._is_succeeded &= result.status.is_succeeded
            self._listener.on_scenario(result)

        self._listener.on_end()

    def _submit_each(
        self,
        executor: ThreadPoolExecutor,
        config_path: str,
    ) -> Callable[[], ScenarioResult]:
        compiler = create_compiler()
        try:
            scenario_obj = load(config_path)
            scenario = compiler.compile(scenario_obj, self._arguments)
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
            listener=self._listener,
        ).result
