from __future__ import annotations

import logging

from preacher.core.scenario import ScenarioResult
from preacher.report.log import LoggingReporter
from . import Listener


class LoggingListener(Listener):

    def __init__(self, reporter: LoggingReporter):
        self._reporter = reporter

    def on_scenario(self, result: ScenarioResult) -> None:
        self._reporter.show_scenario_result(result)

    @staticmethod
    def from_logger(logger: logging.Logger) -> LoggingListener:
        reporter = LoggingReporter(logger)
        return LoggingListener(reporter)
