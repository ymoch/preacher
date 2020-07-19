"""Preacher CLI."""

import logging
import os
import sys
from itertools import chain
from typing import Iterable

from preacher.compilation.scenario import create_scenario_compiler
from preacher.compilation.yaml import load_all, load_all_from_path
from preacher.core.scenario import ScenarioRunner, MergingListener
from preacher.presentation.listener import LoggingListener, ReportingListener
from .log import get_logger
from .option import parse_args

LOGGER = get_logger(__name__, logging.WARNING)
REPORT_LOGGER_NAME = 'preacher-cli.report.logger'


def _main() -> None:
    args = parse_args(environ=os.environ)

    runner = ScenarioRunner(
        base_url=args.url,
        retry=args.retry,
        delay=args.delay,
        timeout=args.timeout,
    )

    if args.scenario:
        objs: Iterable[object] = chain.from_iterable(
            load_all_from_path(path) for path in args.scenario
        )
    else:
        objs = load_all(sys.stdin)

    compiler = create_scenario_compiler()
    scenarios = chain.from_iterable(
        compiler.compile_flattening(obj, arguments=args.argument)
        for obj in objs
    )

    listener = MergingListener()
    listener.append(LoggingListener.from_logger(
        get_logger(REPORT_LOGGER_NAME, args.level)
    ))
    if args.report:
        listener.append(ReportingListener.from_path(args.report))

    with args.concurrent_executor_factory(args.concurrency) as executor:
        status = runner.run(executor, scenarios, listener=listener)

    if not status.is_succeeded:
        sys.exit(1)


def main():
    """Main."""
    try:
        _main()
    except Exception as error:
        LOGGER.exception('%s', error)
        sys.exit(2)
