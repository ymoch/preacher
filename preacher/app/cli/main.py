"""Preacher CLI."""

from __future__ import annotations

import argparse
import logging
import sys

from preacher import __version__ as VERSION
from preacher.presentation.logging import LoggingPresentation
from .application import Application


HANDLER = logging.StreamHandler()
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(HANDLER)


LOGGING_LEVEL_MAP = {
    'skipped': logging.DEBUG,
    'success': logging.INFO,
    'unstable': logging.WARN,
    'failure': logging.ERROR,
}


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
        'conf',
        nargs='+',
        help='config file paths'
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
        default='http://localhost:5000',
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
        help='max retry count',
        default=0,
    )
    parser.add_argument(
        '-c', '--scenario-concurrency',
        type=int,
        help='concurrency for scenarios',
        default=1,
    )

    return parser.parse_args()


def main() -> None:
    """Main."""
    args = parse_args()

    level = LOGGING_LEVEL_MAP[args.level]
    HANDLER.setLevel(level)
    LOGGER.setLevel(level)

    view = LoggingPresentation(LOGGER)
    base_url = args.url
    retry = args.retry
    app = Application(view=view, base_url=base_url, retry=retry)

    config_paths = args.conf
    scenario_concurrency = args.scenario_concurrency
    app.run_concurrently(config_paths, concurrency=scenario_concurrency)

    if not app.is_succeeded:
        sys.exit(1)
