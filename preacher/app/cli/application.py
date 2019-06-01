from __future__ import annotations

from multiprocessing import Pool
from typing import Callable, Iterable, Iterator

import ruamel.yaml as yaml

from preacher.core.scenario_running import ScenarioResult, run_scenario
from preacher.compilation.scenario import ScenarioCompiler
from preacher.presentation.logging import LoggingPresentation


MapFunction = Callable[
    [
        Callable[[str], ScenarioResult],
        Iterable[str]
    ],
    Iterator[ScenarioResult]
]


class Application:
    def __init__(
        self: Application,
        base_url: str,
        view: LoggingPresentation,
    ) -> None:
        self._view = view
        self._base_url = base_url

        self._scenario_compiler = ScenarioCompiler()
        self._is_succeeded = True

    @property
    def is_succeeded(self: Application) -> bool:
        return self._is_succeeded

    def run(
        self: Application,
        config_paths: Iterable[str],
        map_func: MapFunction = map,
    ) -> None:
        results = map_func(self._run_each, config_paths)
        for result in results:
            self._is_succeeded &= result.status.is_succeeded
            self._view.show_scenario_result(result)

    def run_concurrently(
        self: Application,
        config_paths: Iterable[str],
        concurrency: int,
    ) -> None:
        with Pool(concurrency) as pool:
            self.run(config_paths, map_func=pool.imap)

    def _run_each(self: Application, config_path: str) -> ScenarioResult:
        with open(config_path) as config_file:
            config = yaml.safe_load(config_file)
        scenario = self._scenario_compiler.compile(config)
        return run_scenario(scenario, base_url=self._base_url)
