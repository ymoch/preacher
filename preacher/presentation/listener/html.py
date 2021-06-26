from typing import List, Optional

from preacher.core.request import Response, ExecutionReport
from preacher.core.scenario import ScenarioResult
from preacher.core.scheduling import Listener
from preacher.core.status import Status
from preacher.presentation.html import HtmlReporter


class HtmlReportingListener(Listener):
    def __init__(self, reporter: HtmlReporter):
        self._reporter = reporter
        self._results: List[ScenarioResult] = []

    def on_execution(self, execution: ExecutionReport, response: Optional[Response]) -> None:
        if not response:
            return
        self._reporter.export_response(execution, response)

    def on_scenario(self, result: ScenarioResult) -> None:
        self._results.append(result)

    def on_end(self, status: Status) -> None:
        self._reporter.export_results(self._results)


def create_html_reporting_listener(path: str):
    reporter = HtmlReporter(path)
    return HtmlReportingListener(reporter)
