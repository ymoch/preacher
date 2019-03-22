"""Logger presentation."""

from __future__ import annotations

import contextlib
import logging
import io
from typing import Iterator, Optional

from preacher.core.verification import Status, Verification
from preacher.core.response_description import ResponseVerification
from preacher.core.scenario import ScenarioVerification


_LEVEL_MAP = {
    Status.SUCCESS: logging.INFO,
    Status.UNSTABLE: logging.WARN,
    Status.FAILURE: logging.ERROR,
}


class LoggerPresentation:
    def __init__(self: LoggerPresentation, logger: logging.Logger) -> None:
        self._logger = logger
        self._indent = ''

    def show_scenario_verification(
        self: LoggerPresentation,
        verification: ScenarioVerification,
        label: Optional[str] = None,
    ) -> None:
        status = verification.status
        level = _LEVEL_MAP[status]

        self._log(level, 'Label: %s', verification.label)
        self._log(level, 'Status: %s', status.name)

        with self._nested():
            self.show_verification(
                verification=verification.request,
                label='Request',
            )

            response = verification.response
            if response:
                self.show_response_verification(response)

    def show_response_verification(
        self: LoggerPresentation,
        verification: ResponseVerification,
        label: str = 'Response',
    ) -> None:
        status = verification.status
        level = _LEVEL_MAP[status]
        self._log(level, f'%s: %s', label, status.name)
        with self._nested():
            self.show_verification(
                verification=verification.status_code,
                label='Status Code',
            )
            self.show_verification(
                verification=verification.body,
                label='Body',
                child_label='Description',
            )

    def show_verification(
        self: LoggerPresentation,
        verification: Verification,
        label: str,
        child_label: str = 'Predicate',
    ) -> None:
        status = verification.status
        level = _LEVEL_MAP[status]
        self._log(level, f'%s: %s', label, status.name)
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
    def _nested(self: LoggerPresentation) -> Iterator[None]:
        original = self._indent
        self._indent += '..'
        yield
        self._indent = original
