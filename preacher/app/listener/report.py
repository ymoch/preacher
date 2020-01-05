from __future__ import annotations

from typing import List

from preacher.core.request import Response
from preacher.core.scenario import ScenarioResult
from preacher.report.html import HtmlReporter
from . import Listener


class ReportingListener(Listener):

    def __init__(self, path):
        self._reporter = HtmlReporter(path)
        self._results: List[ScenarioResult] = []

    def on_response(self, response: Response) -> None:
        self._reporter.export_response(response)

    def on_scenario(self, result: ScenarioResult) -> None:
        self._results.append(result)

    def on_end(self) -> None:
        self._reporter.export_results(self._results)
