"""Preacher CLI."""

import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from itertools import chain
from typing import Iterable

from preacher.compilation import (
    create_compiler,
    load_all,
    load_all_from_path,
    CompilationError,
)
from preacher.core.listener import MergingListener
from preacher.core.runner import ScenarioRunner
from preacher.presentation.listener import LoggingListener, ReportingListener
from .log import ColoredFormatter
from .option import parse_args

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

    app = ScenarioRunner(
        base_url=args.url,
        retry=args.retry,
        delay=args.delay,
        timeout=args.timeout,
    )

    if args.scenario:
        objs: Iterable = chain.from_iterable(
            load_all_from_path(path) for path in args.scenario
        )
    else:
        objs = list(load_all(sys.stdin))

    compiler = create_compiler()
    scenarios = (
        compiler.compile(obj, arguments=args.argument)
        for obj in objs
    )

    listener = MergingListener()
    listener.append(LoggingListener.from_logger(LOGGER))
    if args.report:
        listener.append(ReportingListener.from_path(args.report))

    with ThreadPoolExecutor(args.concurrency) as executor:
        status = app.run(executor, scenarios, listener=listener)

    if not status.is_succeeded:
        sys.exit(1)


def main():
    try:
        _main()
    except CompilationError as error:
        LOGGER.critical(
            'Compilation error on node: %s',
            error.render_path(),
        )
        LOGGER.critical('%s', error)
        sys.exit(2)
    except Exception as error:
        LOGGER.exception('%s', error)
        sys.exit(3)
