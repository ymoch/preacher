from __future__ import annotations

from typing import List

from preacher.core.response import Response
from preacher.core.scenario import ScenarioResult
from preacher.presentation.report import Reporter
from . import Listener


class ReportingListener(Listener):

    def __init__(self, reporter: Reporter):
        self._reporter = reporter
        self._results: List[ScenarioResult] = []

    def on_response(self, response: Response) -> None:
        self._reporter.export_response(response)

    def on_scenario(self, result: ScenarioResult) -> None:
        self._results.append(result)

    def on_end(self) -> None:
        self._reporter.export_results(self._results)

    @staticmethod
    def from_path(path: str) -> ReportingListener:
        reporter = Reporter(path)
        return ReportingListener(reporter)
