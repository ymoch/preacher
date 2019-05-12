from __future__ import annotations

from preacher.core.scenario import Scenario
from preacher.presentation.logging import LoggingPresentation


class Application:
    def __init__(
        self: Application,
        base_url: str,
        view: LoggingPresentation,
    ) -> None:
        self._view = view
        self._base_url = base_url
        self._is_succeeded = True

    @property
    def is_succeeded(self: Application) -> bool:
        return self._is_succeeded

    def consume_scenario(self: Application, scenario: Scenario) -> None:
        result = scenario(base_url=self._base_url)

        self._is_succeeded &= result.status.is_succeeded
        self._view.show_scenario_result(result, 'Scenario')
