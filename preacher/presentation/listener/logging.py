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


def create_logging_reporting_listener(
    reporter: Optional[LoggingReporter] = None,
    logger: Optional[logging.Logger] = None,
    logger_name: str = "",
    level: Status = Status.SUCCESS,
    handlers: Optional[Iterable[logging.Handler]] = None,
    formatter: Optional[logging.Formatter] = None,
) -> LoggingReportingListener:
    """
    Create a logging reporting listener.

    Args:
        reporter: A reporter. When given this, the other parameters are ignored.
        logger: A logger where reports logged.
            When given this, `logger_name`, `level`, `handlers` and `formatter` are ignored.
        logger_name: The logger name. When not given, it will be automatically generated.
        level: The minimum level to report.
        handlers: The logging handlers. When given, `formatter` is ignored.
        formatter: The logging formatter.
    """
    reporter = reporter or create_logging_reporter(
        logger=logger,
        logger_name=logger_name,
        level=level,
        handlers=handlers,
        formatter=formatter,
    )
    return LoggingReportingListener(reporter)
