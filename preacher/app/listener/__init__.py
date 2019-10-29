from __future__ import annotations

from abc import abstractmethod

from preacher.core.scenario import ScenarioListener, ScenarioResult


class Listener(ScenarioListener):

    @abstractmethod
    def __enter__(self) -> Listener:
        raise NotImplementedError()

    @abstractmethod
    def __exit__(self, ex_type, ex_value, trace) -> None:
        raise NotImplementedError()

    @abstractmethod
    def on_scenario(self, result: ScenarioResult) -> None:
        raise NotImplementedError()
