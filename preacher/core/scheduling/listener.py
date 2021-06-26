from typing import List, Optional

from preacher.core.request import Response, ExecutionReport
from preacher.core.scenario import ScenarioResult, CaseListener
from preacher.core.status import Status


class Listener(CaseListener):
    """
    Listener interface.
    Default implementations do nothing.
    """

    def on_end(self, status: Status) -> None:
        pass

    def on_scenario(self, result: ScenarioResult) -> None:
        pass


class MergingListener(Listener):
    def __init__(self):
        self._listeners: List[Listener] = []

    def append(self, listener: Listener) -> None:
        self._listeners.append(listener)

    def on_execution(self, execution: ExecutionReport, response: Optional[Response]) -> None:
        for listener in self._listeners:
            listener.on_execution(execution, response)

    def on_scenario(self, result: ScenarioResult) -> None:
        for listener in self._listeners:
            listener.on_scenario(result)

    def on_end(self, status: Status) -> None:
        for listener in self._listeners:
            listener.on_end(status)
