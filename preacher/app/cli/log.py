import logging

from colorama import Fore, Style, init

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
    return f'{Fore.RED}{Style.BRIGHT}{message}{Style.RESET_ALL}'


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
