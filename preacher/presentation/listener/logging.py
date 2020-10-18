from __future__ import annotations

import logging

from preacher.core.scenario import ScenarioResult
from preacher.core.scheduling import Listener
from preacher.core.status import Status
from preacher.presentation.logging import LoggingReporter


class LoggingReportingListener(Listener):

    def __init__(self, reporter: LoggingReporter):
        self._reporter = reporter

    def on_scenario(self, result: ScenarioResult) -> None:
        self._reporter.show_scenario_result(result)

    def on_end(self, status: Status) -> None:
        self._reporter.show_status(status)

    @staticmethod
    def from_logger(logger: logging.Logger) -> LoggingReportingListener:
        reporter = LoggingReporter(logger)
        return LoggingReportingListener(reporter)
