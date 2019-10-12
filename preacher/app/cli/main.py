"""Preacher CLI."""

from __future__ import annotations

import argparse
import logging
import sys
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from preacher import __version__ as VERSION
from preacher.app.application import Application
from preacher.app.listener import Listener
from preacher.app.listener.empty import EmptyListener
from preacher.app.listener.logging import LoggingListener
from preacher.app.listener.report import ReportingListener


DEFAULT_URL = 'http://localhost:5042'
DEFAULT_URL_DESCRIPTION = 'the sample'

HANDLER = logging.StreamHandler()
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(HANDLER)


LOGGING_LEVEL_MAP = {
    'skipped': logging.DEBUG,
    'success': logging.INFO,
    'unstable': logging.WARN,
    'failure': logging.ERROR,
}


def report_to(path: Optional[str] = None) -> Listener:
    if not path:
        return EmptyListener()
    return ReportingListener(path)


def zero_or_positive_int(value: str) -> int:
    int_value = int(value)
    if int_value < 0:
        raise argparse.ArgumentTypeError(
            f"must be positive or 0, given {int_value}"
        )
    return int_value


def positive_float(value: str) -> float:
    float_value = float(value)
    if float_value <= 0.0:
        raise argparse.ArgumentTypeError(
            f"must be positive, given {float_value}"
        )
    return float_value


def zero_or_positive_float(value: str) -> float:
    float_value = float(value)
    if float_value < 0.0:
        raise argparse.ArgumentTypeError(
            f"must be positive or 0, given {float_value}"
        )
    return float_value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'scenario',
        nargs='+',
        help='scenario file paths'
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=VERSION,
    )
    parser.add_argument(
        '-u', '--url',
        metavar='url',
        help='specify the base URL',
        default='http://localhost:5042',
    )
    parser.add_argument(
        '-l', '--level',
        choices=LOGGING_LEVEL_MAP.keys(),
        help='show only above or equal to this level',
        default='success',
    )
    parser.add_argument(
        '-r', '--retry',
        type=zero_or_positive_int,
        metavar='num',
        help='set the max retry count',
        default=0,
    )
    parser.add_argument(
        '-d', '--delay',
        type=zero_or_positive_float,
        metavar='sec',
        help='set the delay between attempts in seconds',
        default=0.1,
    )
    parser.add_argument(
        '-t', '--timeout',
        type=positive_float,
        metavar='sec',
        help='set the request timeout in seconds',
    )
    parser.add_argument(
        '-c', '--concurrency',
        type=int,
        metavar='num',
        help='set the request concurrency',
        default=1,
    )
    parser.add_argument(
        '-R', '--report',
        metavar='dir',
        help='report directory (experimental)',
    )

    return parser.parse_args()


def main() -> None:
    """Main."""
    args = parse_args()

    level = LOGGING_LEVEL_MAP[args.level]
    HANDLER.setLevel(level)
    LOGGER.setLevel(level)

    with ThreadPoolExecutor(args.concurrency) as executor, \
            LoggingListener(LOGGER) as logging_listener, \
            report_to(args.report) as reporting_listener:
        app = Application(
            presentations=[logging_listener, reporting_listener],
            base_url=args.url,
            retry=args.retry,
            delay=args.delay,
            timeout=args.timeout,
        )
        app.run(executor, args.scenario)

    if not app.is_succeeded:
        sys.exit(1)
