from __future__ import annotations

from preacher.core.scenario import Scenario
from preacher.presentation.logger import LoggerPresentation


class Application:
    def __init__(
        self: Application,
        base_url: str,
        view: LoggerPresentation,
    ) -> None:
        self._view = view
        self._base_url = base_url
        self._is_succeeded = True

    @property
    def is_succeeded(self: Application) -> bool:
        return self._is_succeeded

    def consume_scenario(self: Application, scenario: Scenario) -> None:
        verification = scenario(base_url=self._base_url)

        self._is_succeeded &= verification.status.is_succeeded
        self._view.show_scenario_verification(verification, 'Response')
