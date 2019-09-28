from __future__ import annotations

from abc import ABC, abstractmethod

from preacher.core.scenario import ScenarioResult


class Listener(ABC):

    @abstractmethod
    def __enter__(self) -> Listener:
        return self

    @abstractmethod
    def __exit__(self, ex_type, ex_value, trace) -> None:
        pass

    @abstractmethod
    def accept(self, result: ScenarioResult) -> None:
        pass


class EmptyListener(Listener):

    def __enter__(self) -> Listener:
        return super().__enter__()

    def __exit__(self, ex_type, ex_value, trace) -> None:
        return super().__exit__(ex_type, ex_value, trace)

    def accept(self, result: ScenarioResult) -> None:
        pass
