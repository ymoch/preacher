"""Preacher CLI."""

import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from itertools import chain
from typing import Iterable

from preacher.compilation.functional import compile_flattening
from preacher.compilation.scenario import create_scenario_compiler
from preacher.core.scenario import ScenarioRunner, MergingListener
from preacher.presentation.listener import LoggingListener, ReportingListener
from preacher.yaml import load_all, load_all_from_path
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
    compile = partial(compiler.compile, arguments=args.argument)
    scenario_groups = (compile_flattening(compile, obj) for obj in objs)
    scenarios = chain.from_iterable(scenario_groups)

    listener = MergingListener()
    listener.append(LoggingListener.from_logger(
        get_logger(REPORT_LOGGER_NAME, args.level)
    ))
    if args.report:
        listener.append(ReportingListener.from_path(args.report))

    with ThreadPoolExecutor(args.concurrency) as executor:
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
