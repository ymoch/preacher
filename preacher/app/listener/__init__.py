from __future__ import annotations

from preacher.core.scenario import ScenarioListener, ScenarioResult


class Listener(ScenarioListener):

    def on_end(self):
        pass

    def on_scenario(self, result: ScenarioResult) -> None:
        pass
