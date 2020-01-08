from __future__ import annotations

from typing import List

from preacher.core.response import Response
from preacher.core.scenario import ScenarioResult
from . import Listener


class MergingListener(Listener):

    def __init__(self):
        self._listeners: List[Listener] = []

    def append(self, listener: Listener):
        self._listeners.append(listener)

    def on_response(self, response: Response) -> None:
        for listener in self._listeners:
            listener.on_response(response)

    def on_scenario(self, result: ScenarioResult) -> None:
        for listener in self._listeners:
            listener.on_scenario(result)

    def on_end(self):
        for listener in self._listeners:
            listener.on_end()
