"""Logging."""

from logging import Logger, getLogger, CRITICAL

__all__ = ["default_logger"]


def _create_logger() -> Logger:
    logger = getLogger(__name__)
    logger.setLevel(CRITICAL + 1)  # Do nothing for predefined levels.
    return logger


default_logger: Logger = _create_logger()
"""A default logger for Preacher, which does nothing by default."""
