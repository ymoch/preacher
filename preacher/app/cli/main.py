"""Preacher CLI."""

import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from .option import parse_args
from preacher.app.application import Application
from preacher.app.listener import Listener
from preacher.app.listener.empty import EmptyListener
from preacher.app.listener.logging import LoggingListener
from preacher.app.listener.report import ReportingListener


HANDLER = logging.StreamHandler()
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(HANDLER)


def _report_to(path: Optional[str] = None) -> Listener:
    if not path:
        return EmptyListener()
    return ReportingListener(path)


def main() -> None:
    """Main."""
    args = parse_args(environ=os.environ)

    level = args.level
    HANDLER.setLevel(level)
    LOGGER.setLevel(level)

    with ThreadPoolExecutor(args.concurrency) as executor, \
            LoggingListener(LOGGER) as logging_listener, \
            _report_to(args.report) as reporting_listener:
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
