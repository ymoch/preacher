from __future__ import annotations

from typing import List

from preacher.core.request import Response
from preacher.core.scenario import ScenarioResult

from . import Listener


class MergingListener(Listener):

    def __init__(self):
        self._listeners: List[Listener] = []

    def __enter__(self) -> MergingListener:
        self._entered_listeners = [
            listener.__enter__()
            for listener in self._listeners
        ]
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for listener in self._entered_listeners:
            listener.__exit__(exc_type, exc_val, exc_tb)

    def on_scenario(self, result: ScenarioResult) -> None:
        for listener in self._entered_listeners:
            listener.on_scenario(result)

    def on_response(self, response: Response) -> None:
        for listener in self._entered_listeners:
            listener.on_response(response)

    def append(self, listener: Listener):
        self._listeners.append(listener)
