"""Serializing Presentation."""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import TextIO

from preacher.core.scenario import ScenarioResult
from preacher.core.status import Status


class JsonEncoder(json.JSONEncoder):
    def default(self, value):
        if isinstance(value, Status):
            return str(value)
        return json.JSONEncoder.default(self, value)


class SerializingPresentation:

    def __init__(self):
        self._results = []

    def accept(self, result: ScenarioResult) -> None:
        self._results.append(result)

    def dump_json(self, out: TextIO) -> None:
        json.dump(self.serialize(), out, cls=JsonEncoder)

    def serialize(self) -> dict:
        return {
            'scenarios': [asdict(result) for result in self._results],
        }
