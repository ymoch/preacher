"""Preacher CLI."""

import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from itertools import chain
from typing import Iterable

from preacher.compilation import CompilationError, create_compiler
from preacher.core.listener import MergingListener
from preacher.core.runner import ScenarioRunner
from preacher.presentation.listener import LoggingListener, ReportingListener
from preacher.yaml import YamlError, load_all, load_all_from_path
from .log import get_logger
from .option import parse_args

LOGGER = get_logger(__name__, logging.WARNING)


def _main() -> bool:
    """Main."""
    args = parse_args(environ=os.environ)

    runner = ScenarioRunner(
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
        objs = load_all(sys.stdin)

    compiler = create_compiler()
    scenarios = (
        compiler.compile(obj, arguments=args.argument)
        for obj in objs
    )

    listener = MergingListener()
    listener.append(LoggingListener.from_logger(
        get_logger(f'{__name__}.report', args.level)
    ))
    if args.report:
        listener.append(ReportingListener.from_path(args.report))

    with ThreadPoolExecutor(args.concurrency) as executor:
        status = runner.run(executor, scenarios, listener=listener)

    return status.is_succeeded


def main():
    try:
        succeeded = _main()
        if not succeeded:
            sys.exit(1)
    except YamlError as error:
        LOGGER.critical('YAML loading error')
        LOGGER.critical(error)
        sys.exit(2)
    except CompilationError as error:
        LOGGER.critical('Compilation error')
        LOGGER.critical(error)
        sys.exit(2)
    except Exception as error:
        LOGGER.exception('%s', error)
        sys.exit(3)
