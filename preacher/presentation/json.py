"""JSON Presentation."""

from __future__ import annotations

import json
from typing import TextIO

from preacher.core.scenario_running import ScenarioResult


class JsonPresentation:

    def __init__(self, out: TextIO):
        self._out = out
        self._results = []

    def __enter__(self) -> JsonPresentation:
        return self

    def __exit__(self, *args, **kwargs) -> None:
        json.dump(self._results, self._out)

    def accept(self, result: ScenarioResult) -> None:
        self._results.append(result)
