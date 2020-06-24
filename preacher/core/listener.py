from preacher.core.scenario import ScenarioListener, ScenarioResult


class Listener(ScenarioListener):
    """
    Listener interface.
    Default implementations do nothing.
    """

    def on_end(self) -> None:
        pass

    def on_scenario(self, result: ScenarioResult) -> None:
        pass
