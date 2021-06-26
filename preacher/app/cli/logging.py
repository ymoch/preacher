from logging import Logger, StreamHandler, Formatter, LogRecord, getLogger
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL

from colorama import Fore, Style, init

init()


def _default(message: str) -> str:
    return message


def _info(message: str) -> str:
    return f"{Fore.GREEN}{message}{Style.RESET_ALL}"


def _warning(message: str) -> str:
    return f"{Fore.YELLOW}{message}{Style.RESET_ALL}"


def _error(message: str) -> str:
    return f"{Fore.RED}{message}{Style.RESET_ALL}"


def _critical(message: str) -> str:
    return f"{Fore.RED}{Style.BRIGHT}{message}{Style.RESET_ALL}"


_STYLE_FUNC_MAP = {
    INFO: _info,
    WARNING: _warning,
    ERROR: _error,
    CRITICAL: _critical,
}


class ColoredFormatter(Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format(self, record: LogRecord) -> str:
        style_func = _STYLE_FUNC_MAP.get(record.levelno, _default)
        return style_func(super().format(record))


def create_system_logger(verbosity: int) -> Logger:
    level = _verbosity_to_logging_level(verbosity)
    handler = StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(ColoredFormatter(fmt="[%(levelname)s] %(message)s"))
    logger = getLogger(__name__)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger


def _verbosity_to_logging_level(verbosity: int) -> int:
    if verbosity > 1:
        return DEBUG
    if verbosity > 0:
        return INFO
    return WARNING
