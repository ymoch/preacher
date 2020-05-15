import contextlib
import io
import logging
from typing import Iterator

from colorama import Fore, Style, init

from preacher.core.scenario import (
    ScenarioResult,
    CaseResult,
    ResponseVerification,
    Status,
    Verification,
)

init()


def _default(message: str) -> str:
    return message


def _info(message: str) -> str:
    return f'{Fore.GREEN}{message}{Style.RESET_ALL}'


def _warning(message: str) -> str:
    return f'{Fore.YELLOW}{message}{Style.RESET_ALL}'


def _error(message: str) -> str:
    return f'{Fore.RED}{message}{Style.RESET_ALL}'


def _critical(message: str) -> str:
    return f'{Fore.RED}{Fore.BRIGHT}{message}{Style.RESET_ALL}'


_STYLE_FUNC_MAP = {
    logging.INFO: _info,
    logging.WARNING: _warning,
    logging.ERROR: _error,
    logging.CRITICAL: _critical,
}


class ColoredFormatter(logging.Formatter):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format(self, record: logging.LogRecord) -> str:
        style_func = _STYLE_FUNC_MAP.get(record.levelno, _default)
        return style_func(super().format(record))


_LEVEL_MAP = {
    Status.SKIPPED: logging.DEBUG,
    Status.SUCCESS: logging.INFO,
    Status.UNSTABLE: logging.WARN,
    Status.FAILURE: logging.ERROR,
}


class Logger:

    def __init__(self, logger: logging.Logger):
        self._logger = logger
        self._indent = ''

    def show_scenario_result(self, scenario: ScenarioResult) -> None:
        status = scenario.status
        level = _LEVEL_MAP[status]

        label = scenario.label or 'Not labeled scenario'
        self._log(level, '%s: %s', label, status)

        message = scenario.message
        if message:
            with self._nested():
                self._multi_line_message(level, message)

        with self._nested():
            for case in scenario.cases.items:
                self.show_case_result(case)

            for subscenario in scenario.subscenarios.items:
                self.show_scenario_result(subscenario)

        self._log(level, '')

    def show_case_result(self, case: CaseResult) -> None:
        status = case.status
        level = _LEVEL_MAP[status]

        label = case.label or 'Not labeled case'
        self._log(level, '%s: %s', label, status)
        with self._nested():
            self.show_verification(
                verification=case.execution,
                label='Execution',
            )

            response = case.response
            if response:
                self.show_response_verification(response)

    def show_response_verification(
        self,
        verification: ResponseVerification,
        label: str = 'Response',
    ) -> None:
        status = verification.status
        level = _LEVEL_MAP[status]
        self._log(level, '%s: %s', label, status)
        with self._nested():
            self.show_verification(
                verification=verification.status_code,
                label='Status Code',
            )
            self.show_verification(
                verification=verification.headers,
                label='Headers',
                child_label='Description',
            )
            self.show_verification(
                verification=verification.body,
                label='Body',
                child_label='Description',
            )

    def show_verification(
        self,
        verification: Verification,
        label: str,
        child_label: str = 'Predicate',
    ) -> None:
        status = verification.status
        level = _LEVEL_MAP[status]
        self._log(level, '%s: %s', label, status)
        message = verification.message
        if message:
            with self._nested():
                self._multi_line_message(level, message)

        with self._nested():
            for idx, child in enumerate(verification.children):
                self.show_verification(child, f'{child_label} {idx + 1}')

    def _log(self, level: int, message: str, *args) -> None:
        self._logger.log(level, self._indent + message, *args)

    def _multi_line_message(self, level: int, message: str) -> None:
        for line in io.StringIO(message):
            self._log(level, line.rstrip())

    @contextlib.contextmanager
    def _nested(self) -> Iterator[None]:
        original = self._indent
        self._indent += '..'
        yield
        self._indent = original
