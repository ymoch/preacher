from __future__ import annotations

import logging
from typing import Iterable, Optional

from preacher.core.scenario import ScenarioResult
from preacher.core.scheduling import Listener
from preacher.core.status import Status
from preacher.presentation.logging import LoggingReporter, create_logging_reporter


class LoggingReportingListener(Listener):
    def __init__(self, reporter: LoggingReporter):
        self._reporter = reporter

    def on_scenario(self, result: ScenarioResult) -> None:
        self._reporter.show_scenario_result(result)

    def on_end(self, status: Status) -> None:
        self._reporter.show_status(status)

    @staticmethod
    def from_logger(logger: logging.Logger) -> LoggingReportingListener:
        # HACK remove this function.
        reporter = LoggingReporter(logger)
        return LoggingReportingListener(reporter)


def create_logging_reporting_listener(
    reporter: Optional[LoggingReporter] = None,
    logger: Optional[logging.Logger] = None,
    logger_name: str = "",
    level: Status = Status.SUCCESS,
    handlers: Optional[Iterable[logging.Handler]] = None,
) -> LoggingReportingListener:
    reporter = reporter or create_logging_reporter(
        logger=logger,
        logger_name=logger_name,
        level=level,
        handlers=handlers,
    )
    return LoggingReportingListener(reporter)
