"""Preacher CLI View."""

import contextlib
import logging
import io

from preacher.core.verification import Status, Verification
from preacher.core.scenario import ResponseVerification


_LEVEL_MAP = {
    Status.SUCCESS: logging.INFO,
    Status.UNSTABLE: logging.WARN,
    Status.FAILURE: logging.ERROR,
}


class LoggingView:
    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger
        self._indent = ''

    def show_response_verification(
        self,
        verification: ResponseVerification,
        label: str,
    ) -> None:
        status = verification.status
        level = _LEVEL_MAP[status]
        self._log(level, f'{label}: {status.name}')
        with self._nested():
            self.show_verification(verification.body, 'Body')

    def show_verification(
        self,
        verification: Verification,
        label: str,
    ) -> None:
        status = verification.status
        level = _LEVEL_MAP[status]
        self._log(level, f'{label}: {status.name}')
        message = verification.message
        if message:
            for line in io.StringIO(message):
                self._log(level, line.rstrip())

        with self._nested():
            for idx, child in enumerate(verification.children):
                self.show_verification(child, f'Predicate {idx + 1}')

    def _log(self, level: int, message: str, *args) -> None:
        self._logger.log(level, self._indent + message, *args)

    @contextlib.contextmanager
    def _nested(self):
        original = self._indent
        self._indent += '  '
        yield
        self._indent = original
