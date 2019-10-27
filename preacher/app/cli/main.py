"""Preacher CLI."""

from __future__ import annotations

import logging
import sys
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from preacher.app.application import Application
from preacher.app.cli.option import parse_args, LOGGING_LEVEL_MAP
from preacher.app.listener import Listener
from preacher.app.listener.empty import EmptyListener
from preacher.app.listener.logging import LoggingListener
from preacher.app.listener.report import ReportingListener


DEFAULT_URL = 'http://localhost:5042'
DEFAULT_URL_DESCRIPTION = 'the sample'

HANDLER = logging.StreamHandler()
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(HANDLER)


def report_to(path: Optional[str] = None) -> Listener:
    if not path:
        return EmptyListener()
    return ReportingListener(path)


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
