from __future__ import annotations

from abc import ABC, abstractmethod

from preacher.core.scenario import ScenarioResult


class Listener(ABC):

    @abstractmethod
    def __enter__(self) -> Listener:
        raise NotImplementedError()

    @abstractmethod
    def __exit__(self, ex_type, ex_value, trace) -> None:
        raise NotImplementedError()

    @abstractmethod
    def accept(self, result: ScenarioResult) -> None:
        raise NotImplementedError()
