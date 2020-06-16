"""Preacher CLI."""

import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from itertools import chain
from typing import Iterable

from preacher.app.cli.option import parse_args
from preacher.compilation.error import CompilationError, render_path
from preacher.compilation.factory import create_compiler
from preacher.compilation.yaml import load_all, load_all_from_path
from preacher.core.listener.log import LoggingListener
from preacher.core.listener.merging import MergingListener
from preacher.core.listener.report import ReportingListener
from preacher.core.runner import ScenarioRunner
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
            render_path(error.path),
        )
        LOGGER.critical('%s', error)
        sys.exit(2)
    except Exception as error:
        LOGGER.exception('%s', error)
        sys.exit(3)
