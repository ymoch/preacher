"""Preacher CLI View."""

import contextlib
import logging

from preacher.core.verification import Status, Verification


_LEVEL_MAP = {
    Status.SUCCESS: logging.INFO,
    Status.UNSTABLE: logging.WARN,
    Status.FAILURE: logging.ERROR,
}


class LoggingView:
    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger
        self._prefix = ''

    def show_verification(
        self,
        verification: Verification,
        label: str,
    ) -> None:
        status = verification.status
        level = _LEVEL_MAP[status]
        self._log(level, f'{label}: {status.name}')
        if status.is_succeeded:
            return

        message = verification.message
        for line in message.split('\n') if message else []:
            self._log(level, line)

        with self._scope('>>> '):
            for idx, child in enumerate(verification.children):
                self.show_verification(child, f'Predicate {idx + 1}')

    def _log(self, level: int, message: str, *args) -> None:
        self._logger.log(level, self._prefix + message, *args)

    @contextlib.contextmanager
    def _scope(self, prefix: str):
        original = self._prefix
        self._prefix += prefix
        yield
        self._prefix = original
