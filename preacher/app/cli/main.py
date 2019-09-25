"""Preacher CLI."""

from __future__ import annotations

import argparse
import logging
import sys

import jinja2

from preacher import __version__ as VERSION
from preacher.presentation.logging import LoggingPresentation
from preacher.presentation.serialization import SerializingPresentation
from .application import Application


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
        '-c', '--scenario-concurrency',
        type=int,
        metavar='num',
        help='concurrency for scenarios',
        default=1,
    )
    parser.add_argument(
        '-j', '--json-dump',
        type=argparse.FileType('w'),
        metavar='file',
        help='result dump file (JSON)',
    )
    parser.add_argument(
        '-H', '--report-html',
        type=argparse.FileType('w'),
        metavar='file',
        help='report HTML file',
    )

    return parser.parse_args()


def main() -> None:
    """Main."""
    args = parse_args()

    level = LOGGING_LEVEL_MAP[args.level]
    HANDLER.setLevel(level)
    LOGGER.setLevel(level)

    serializing_presentation = SerializingPresentation()
    presentations = [
        LoggingPresentation(LOGGER),
        serializing_presentation,
    ]

    base_url = args.url
    retry = args.retry
    app = Application(
        presentations=presentations,
        base_url=base_url,
        retry=retry,
    )

    scenario_paths = args.scenario
    scenario_concurrency = args.scenario_concurrency
    app.run_concurrently(scenario_paths, concurrency=scenario_concurrency)

    if args.json_dump:
        serializing_presentation.dump_json(args.json_dump)

    if args.report_html:
        env = jinja2.Environment(
            loader=jinja2.PackageLoader('preacher', 'resources/html'),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
        env.get_template('index.html').stream(
            **serializing_presentation.serialize()
        ).dump(args.report_html)

    if not app.is_succeeded:
        sys.exit(1)
