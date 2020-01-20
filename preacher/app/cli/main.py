"""Preacher CLI."""

import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor

from preacher.core.scenariorunner import ScenarioRunner
from preacher.app.cli.option import parse_args
from preacher.compilation.factory import create_compiler
from preacher.compilation.yaml import load
from preacher.listener.log import LoggingListener
from preacher.listener.merging import MergingListener
from preacher.listener.report import ReportingListener
from preacher.presentation.log import ColoredFormatter

FORMATTER = ColoredFormatter()
HANDLER = logging.StreamHandler()
HANDLER.setFormatter(FORMATTER)
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(HANDLER)


def _main() -> None:
    """Main."""
    args = parse_args(environ=os.environ)

    level = args.level
    HANDLER.setLevel(level)
    LOGGER.setLevel(level)

    listener = MergingListener()
    listener.append(LoggingListener.from_logger(LOGGER))
    if args.report:
        listener.append(ReportingListener.from_path(args.report))

    compiler = create_compiler()
    scenarios = (
        compiler.compile(load(path), arguments=args.argument)
        for path in args.scenario
    )

    app = ScenarioRunner(
        base_url=args.url,
        retry=args.retry,
        delay=args.delay,
        timeout=args.timeout,
        listener=listener,
    )
    with ThreadPoolExecutor(args.concurrency) as executor:
        app.run(executor, scenarios)

    if not app.is_succeeded:
        sys.exit(1)


def main():
    try:
        _main()
    except Exception as error:
        LOGGER.exception('%s', error)
        sys.exit(2)
