"""CLI Options."""

import logging
import re
import shlex
from argparse import ArgumentParser, ArgumentTypeError, Namespace
from enum import Enum
from typing import List, Mapping, Optional, Tuple

from yaml import safe_load
from yaml.error import MarkedYAMLError

from preacher import __version__ as _version


class Level(Enum):
    SKIPPED = logging.DEBUG
    SUCCESS = logging.INFO
    UNSTABLE = logging.WARN
    FAILURE = logging.ERROR

    def __str__(self):
        return self.name.lower()


_LEVEL_MAP: Mapping[str, Level] = {str(level): level for level in Level}


_ENV_PREFIX = 'PREACHER_CLI_'
_ENV_BASE_URL = f'{_ENV_PREFIX}BASE_URL'
_ENV_ARGUMENT = f'{_ENV_PREFIX}ARGUMENT'
_ENV_LEVEL = f'{_ENV_PREFIX}LEVEL'
_ENV_RETRY = f'{_ENV_PREFIX}RETRY'
_ENV_DELAY = f'{_ENV_PREFIX}DELAY'
_ENV_TIMEOUT = f'{_ENV_PREFIX}TIMEOUT'
_ENV_CONCURRENCY = f'{_ENV_PREFIX}CONCURRENCY'
_ENV_REPORT = f'{_ENV_PREFIX}REPORT'

_DEFAULT_ENV_MAP: Mapping[str, Optional[str]] = {
    _ENV_BASE_URL: '',
    _ENV_ARGUMENT: '',
    _ENV_LEVEL: 'success',
    _ENV_RETRY: '0',
    _ENV_DELAY: '0.1',
    _ENV_TIMEOUT: None,
    _ENV_CONCURRENCY: '1',
    _ENV_REPORT: None,
}


def positive_int(value: str) -> int:
    int_value = int(value)
    if int_value <= 0:
        raise ArgumentTypeError(f'must be positive or 0, given {int_value}')
    return int_value


def zero_or_positive_int(value: str) -> int:
    int_value = int(value)
    if int_value < 0:
        raise ArgumentTypeError(f'must be positive or 0, given {int_value}')
    return int_value


def positive_float(value: str) -> float:
    float_value = float(value)
    if float_value <= 0.0:
        raise ArgumentTypeError(f'must be positive, given {float_value}')
    return float_value


def zero_or_positive_float(value: str) -> float:
    float_value = float(value)
    if float_value < 0.0:
        raise ArgumentTypeError(f'must be positive or 0, given {float_value}')
    return float_value


def level(value: str) -> Level:
    result = _LEVEL_MAP.get(value)
    if not result:
        raise ArgumentTypeError(f'invalid level: {value}')
    return result


def argument(value: str) -> Tuple[str, object]:
    match = re.match(r'^([^=]+)=(.*)$', value)
    if not match:
        raise ArgumentTypeError(f'Invalid format argument: {value}')

    key = match.group(1)
    try:
        value = safe_load(match.group(2))
    except MarkedYAMLError as error:
        raise ArgumentTypeError(f'Invalid YAML format. {error}')

    return key, value


def parse_args(
    argv: Optional[List[str]] = None,
    environ: Optional[Mapping[str, str]] = None,
) -> Namespace:
    environ = environ or {}
    defaults = {
        name: environ.get(name) or value
        for (name, value) in _DEFAULT_ENV_MAP.items()
    }

    parser = ArgumentParser()
    parser.add_argument(
        'scenario',
        nargs='*',
        metavar='path',
        help='scenario file paths. When given none, stdin is used instead.'
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=_version,
    )
    parser.add_argument(
        '-u', '--url',
        metavar='url',
        help='specify the base URL',
        default=defaults[_ENV_BASE_URL],
    )
    parser.add_argument(
        '-a', '--argument',
        type=argument,
        metavar='arg',
        nargs='*',
        help='scenario arguments in format "NAME=VALUE" (experimental)',
    )
    parser.add_argument(
        '-l', '--level',
        type=level,
        choices=Level,
        help='show only above or equal to this level',
        default=defaults[_ENV_LEVEL],
    )
    parser.add_argument(
        '-r', '--retry',
        type=zero_or_positive_int,
        metavar='num',
        help='set the max retry count',
        default=defaults[_ENV_RETRY],
    )
    parser.add_argument(
        '-d', '--delay',
        type=zero_or_positive_float,
        metavar='sec',
        help='set the delay between attempts in seconds',
        default=defaults[_ENV_DELAY],
    )
    parser.add_argument(
        '-t', '--timeout',
        type=positive_float,
        metavar='sec',
        help='set the request timeout in seconds',
        default=defaults[_ENV_TIMEOUT],
    )
    parser.add_argument(
        '-c', '--concurrency',
        type=positive_int,
        metavar='num',
        help='set the request concurrency',
        default=defaults[_ENV_CONCURRENCY],
    )
    parser.add_argument(
        '-R', '--report',
        metavar='dir',
        help='report directory',
        default=defaults[_ENV_REPORT],
    )

    args = parser.parse_args(argv)
    args.level = args.level.value

    arguments = args.argument
    if arguments is None:
        try:
            arguments = [
                argument(arg)
                for arg in shlex.split(defaults[_ENV_ARGUMENT] or '')
            ]
        except ValueError as error:
            raise RuntimeError(f'Failed to parse {_ENV_ARGUMENT}: {error}')
    args.argument = dict(arguments)

    return args
