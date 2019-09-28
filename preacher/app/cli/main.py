"""Preacher CLI."""

from __future__ import annotations

import argparse
import logging
import sys
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
        help='max retry count',
        default=0,
    )
    parser.add_argument(
        '-d', '--delay',
        type=float,
        metavar='sec',
        help='delay in seconds between attempts',
        default=0.1,
    )
    parser.add_argument(
        '-c', '--scenario-concurrency',
        type=int,
        metavar='num',
        help='concurrency for scenarios',
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

    with LoggingListener(LOGGER) as logging_listener, \
            report_to(args.report) as reporting_listener:
        app = Application(
            presentations=[logging_listener, reporting_listener],
            base_url=args.url,
            retry=args.retry,
            delay=args.delay,
        )
        app.run_concurrently(
            args.scenario,
            concurrency=args.scenario_concurrency,
        )

    if not app.is_succeeded:
        sys.exit(1)
