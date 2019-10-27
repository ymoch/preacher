"""CLI Options."""

import logging
from argparse import ArgumentParser, ArgumentTypeError, Namespace
from typing import List, Mapping, Optional

from preacher import __version__ as version


_LOGGING_LEVEL_MAP: Mapping[str, int] = {
    'skipped': logging.DEBUG,
    'success': logging.INFO,
    'unstable': logging.WARN,
    'failure': logging.ERROR,
}


_ENV_PREFIX = 'PREACHER_'
_DEFAULT_ENV_MAP: Mapping[str, Optional[str]] = {
    f'{_ENV_PREFIX}URL': 'http://localhost:5042',
    f'{_ENV_PREFIX}LEVEL': 'success',
    f'{_ENV_PREFIX}RETRY': '0',
    f'{_ENV_PREFIX}DELAY': '0.1',
    f'{_ENV_PREFIX}TIMEOUT': None,
    f'{_ENV_PREFIX}CONCURRENCY': '1',
    f'{_ENV_PREFIX}REPORT': None,
}


def positive_int(value: str) -> int:
    int_value = int(value)
    if int_value <= 0:
        raise ArgumentTypeError(f"must be positive or 0, given {int_value}")
    return int_value


def zero_or_positive_int(value: str) -> int:
    int_value = int(value)
    if int_value < 0:
        raise ArgumentTypeError(f"must be positive or 0, given {int_value}")
    return int_value


def positive_float(value: str) -> float:
    float_value = float(value)
    if float_value <= 0.0:
        raise ArgumentTypeError(f"must be positive, given {float_value}")
    return float_value


def zero_or_positive_float(value: str) -> float:
    float_value = float(value)
    if float_value < 0.0:
        raise ArgumentTypeError(f"must be positive or 0, given {float_value}")
    return float_value


def parse_args(args: Optional[List[str]] = None) -> Namespace:
    env_map = _DEFAULT_ENV_MAP

    parser = ArgumentParser()
    parser.add_argument(
        'scenario',
        nargs='+',
        help='scenario file paths'
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=version,
    )
    parser.add_argument(
        '-u', '--url',
        metavar='url',
        help='specify the base URL',
        default=env_map.get(f'{_ENV_PREFIX}URL'),
    )
    parser.add_argument(
        '-l', '--level',
        choices=_LOGGING_LEVEL_MAP.keys(),
        help='show only above or equal to this level',
        default=env_map.get(f'{_ENV_PREFIX}LEVEL'),
    )
    parser.add_argument(
        '-r', '--retry',
        type=zero_or_positive_int,
        metavar='num',
        help='set the max retry count',
        default=env_map.get(f'{_ENV_PREFIX}RETRY'),
    )
    parser.add_argument(
        '-d', '--delay',
        type=zero_or_positive_float,
        metavar='sec',
        help='set the delay between attempts in seconds',
        default=env_map.get(f'{_ENV_PREFIX}DELAY'),
    )
    parser.add_argument(
        '-t', '--timeout',
        type=positive_float,
        metavar='sec',
        help='set the request timeout in seconds',
        default=env_map.get(f'{_ENV_PREFIX}TIMEOUT'),
    )
    parser.add_argument(
        '-c', '--concurrency',
        type=positive_int,
        metavar='num',
        help='set the request concurrency',
        default=env_map.get(f'{_ENV_PREFIX}CONCURRENCY'),
    )
    parser.add_argument(
        '-R', '--report',
        metavar='dir',
        help='report directory (experimental)',
        default=env_map.get(f'{_ENV_PREFIX}REPORT'),
    )

    parsed = parser.parse_args(args)
    parsed.level = _LOGGING_LEVEL_MAP[parsed.level]

    return parsed
