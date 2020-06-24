from __future__ import annotations

import logging

from preacher.core.listener import Listener
from preacher.core.scenario import ScenarioResult
from preacher.presentation.log import Logger


class LoggingListener(Listener):

    def __init__(self, reporter: Logger):
        self._reporter = reporter

    def on_scenario(self, result: ScenarioResult) -> None:
        self._reporter.show_scenario_result(result)

    @staticmethod
    def from_logger(logger: logging.Logger) -> LoggingListener:
        reporter = Logger(logger)
        return LoggingListener(reporter)
