from __future__ import annotations

from preacher.core.scenario import ScenarioResult
from . import Listener


class EmptyListener(Listener):

    def __enter__(self) -> EmptyListener:
        return self

    def __exit__(self, ex_type, ex_value, trace) -> None:
        pass

    def accept(self, result: ScenarioResult) -> None:
        pass
