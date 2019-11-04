"""Preacher CLI."""

import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor

from preacher.app.application import Application
from preacher.app.cli.logging import ColoredFormatter
from preacher.app.cli.option import parse_args
from preacher.app.listener.logging import LoggingListener
from preacher.app.listener.merging import MergingListener
from preacher.app.listener.report import ReportingListener


FORMATTER = ColoredFormatter()
HANDLER = logging.StreamHandler()
HANDLER.setFormatter(FORMATTER)
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(HANDLER)


def main() -> None:
    """Main."""
    args = parse_args(environ=os.environ)

    level = args.level
    HANDLER.setLevel(level)
    LOGGER.setLevel(level)

    listener = MergingListener()
    listener.append(LoggingListener(LOGGER))
    if args.report:
        listener.append(ReportingListener(args.report))

    with ThreadPoolExecutor(args.concurrency) as executor:
        app = Application(
            base_url=args.url,
            retry=args.retry,
            delay=args.delay,
            timeout=args.timeout,
            listener=listener,
        )
        app.run(executor, args.scenario)

    if not app.is_succeeded:
        sys.exit(1)
