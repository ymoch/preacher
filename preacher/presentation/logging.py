import contextlib
import io
import logging
import sys
import uuid
from typing import Iterable, Iterator, Optional

from preacher.core.request import ExecutionReport
from preacher.core.scenario import ScenarioResult, CaseResult
from preacher.core.status import Status
from preacher.core.verification import ResponseVerification, Verification

_LEVEL_MAP = {
    Status.SKIPPED: logging.DEBUG,
    Status.SUCCESS: logging.INFO,
    Status.UNSTABLE: logging.WARN,
    Status.FAILURE: logging.ERROR,
}


class LoggingReporter:
    def __init__(self, logger: logging.Logger):
        self._logger = logger
        self._indent = ""

    def show_scenario_result(self, scenario: ScenarioResult) -> None:
        status = scenario.status
        level = _LEVEL_MAP[status]

        label = scenario.label or "Not labeled scenario"
        self._log(level, "%s: %s", label, status)

        message = scenario.message
        if message:
            with self._nesting():
                self._multi_line_message(level, message)

        with self._nesting():
            for case in scenario.cases.items:
                self.show_case_result(case)

            for subscenario in scenario.subscenarios.items:
                self.show_scenario_result(subscenario)

    def show_case_result(self, case: CaseResult) -> None:
        status = case.status
        level = _LEVEL_MAP[status]

        label = case.label or "Not labeled case"
        self._log(level, "%s: %s", label, status)
        with self._nesting():
            self.show_execution(case.execution)

            response = case.response
            if response:
                self.show_response_verification(response)

    def show_execution(self, execution: ExecutionReport) -> None:
        status = execution.status
        level = _LEVEL_MAP[status]

        self._log(level, "Execution: %s", status)
        if execution.message:
            with self._nesting():
                self._multi_line_message(level, execution.message)

    def show_response_verification(
        self,
        verification: ResponseVerification,
        label: str = "Response",
    ) -> None:
        status = verification.status
        level = _LEVEL_MAP[status]
        self._log(level, "%s: %s", label, status)
        with self._nesting():
            self.show_verification(
                verification=verification.status_code,
                label="Status Code",
            )
            self.show_verification(
                verification=verification.headers,
                label="Headers",
                child_label="Description",
            )
            self.show_verification(
                verification=verification.body,
                label="Body",
                child_label="Description",
            )

    def show_verification(
        self,
        verification: Verification,
        label: str,
        child_label: str = "Predicate",
    ) -> None:
        status = verification.status
        level = _LEVEL_MAP[status]
        self._log(level, "%s: %s", label, status)
        message = verification.message
        if message:
            with self._nesting():
                self._multi_line_message(level, message)

        with self._nesting():
            for idx, child in enumerate(verification.children):
                self.show_verification(child, f"{child_label} {idx + 1}")

    def show_status(self, status: Status) -> None:
        level = _LEVEL_MAP[status]
        self._log(level, "%s", status)

    def _log(self, level: int, message: str, *args) -> None:
        self._logger.log(level, self._indent + message, *args)

    def _multi_line_message(self, level: int, message: str) -> None:
        for line in io.StringIO(message):
            self._log(level, line.rstrip())

    @contextlib.contextmanager
    def _nesting(self) -> Iterator[None]:
        original = self._indent
        self._indent += ".."
        yield
        self._indent = original


def create_logging_reporter(
    logger: Optional[logging.Logger] = None,
    logger_name: str = "",
    level: Status = Status.SUCCESS,
    handlers: Optional[Iterable[logging.Handler]] = None,
    formatter: Optional[logging.Formatter] = None,
) -> LoggingReporter:
    """
    Create a logging reporter.

    Args:
        logger: A logger where reports logged. When given this, the other parameters are ignored.
        logger_name: The logger name. When not given, it will be automatically generated.
        level: The minimum level to report.
        handlers: The logging handlers. When given, `formatter` is ignored.
        formatter: The logging formatter.
    """
    if not logger:
        logging_level = _status_to_logging_level(level)
        logger = logging.getLogger(logger_name or str(uuid.uuid4()))
        logger.setLevel(logging_level)

        if not handlers:
            default_handler = logging.StreamHandler(sys.stdout)
            default_handler.setLevel(logging_level)
            if formatter:
                default_handler.setFormatter(formatter)
            handlers = (default_handler,)
        for handler in handlers:
            logger.addHandler(handler)

    return LoggingReporter(logger)


def _status_to_logging_level(level: Status) -> int:
    if level is Status.SKIPPED:
        return logging.DEBUG
    if level is Status.SUCCESS:
        return logging.INFO
    if level is Status.UNSTABLE:
        return logging.WARNING
    return logging.ERROR
