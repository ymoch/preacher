import sys
from concurrent.futures import Executor
from itertools import chain
from logging import DEBUG, INFO, WARNING, Logger, StreamHandler, getLogger
from typing import Sequence, Optional, Callable, Iterator

from preacher.compilation.argument import Arguments
from preacher.compilation.scenario import create_scenario_compiler
from preacher.compilation.yaml import load_all, load_all_from_path
from preacher.core.scenario import ScenarioRunner, Listener, MergingListener
from preacher.presentation.listener import (
    LoggingReportingListener,
    HtmlReportingListener,
)
from .logging import ColoredFormatter

REPORT_LOGGER_NAME = 'preacher.cli.report.logging'


def app(
    paths: Sequence[str],
    base_url: str,
    arguments: Arguments,
    level: int,
    report_dir: Optional[str],
    retry: int,
    delay: float,
    timeout: Optional[float],
    concurrency: int,
    executor_factory: Callable[[int], Executor],
    verbosity: int,
):
    logger = _create_system_logger(verbosity=verbosity)

    logger.debug(
        'Running condition\n'
        '  Paths: %s\n'
        '  Arguments: %s\n'
        '  Base URL: %s\n'
        '  Logging report level: %d\n'
        '  Reporting directory path: %s\n'
        '  Max retry count: %d\n'
        '  Delay between attempts in seconds: %s\n'
        '  Timeout in seconds: %s\n'
        '  Concurrency: %s\n'
        '  Executor: %s\n'
        '  Verbosity: %d',
        paths,
        arguments,
        base_url,
        level,
        report_dir,
        retry,
        delay,
        timeout,
        concurrency,
        executor_factory,
        verbosity
    )

    objs = _load_objs(paths, logger=logger)
    compiler = create_scenario_compiler()
    scenarios = chain.from_iterable(
        compiler.compile_flattening(obj, arguments=arguments)
        for obj in objs
    )

    runner = ScenarioRunner(
        base_url=base_url,
        retry=retry,
        delay=delay,
        timeout=timeout
    )
    listener = _create_listener(level, report_dir)
    try:
        logger.info("Start running scenarios.")
        with executor_factory(concurrency) as executor:
            status = runner.run(executor, scenarios, listener=listener)
    except Exception as error:
        logger.exception(error)
        sys.exit(3)
    logger.info("End running scenarios.")

    if not status.is_succeeded:
        sys.exit(1)


def _create_system_logger(name: str = __name__, verbosity: int = 0) -> Logger:
    level = _select_level(verbosity)

    handler = StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(ColoredFormatter(fmt='[%(levelname)s] %(message)s'))
    logger = getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger


def _select_level(verbosity: int) -> int:
    if verbosity > 1:
        return DEBUG
    if verbosity > 0:
        return INFO
    return WARNING


def _load_objs(paths: Sequence[str], logger: Logger) -> Iterator[object]:
    if not paths:
        logger.info('Load scenarios from stdin.')
        return load_all(sys.stdin)
    return chain.from_iterable(load_all_from_path(path) for path in paths)


def _create_listener(level: int, report_dir: Optional[str]) -> Listener:
    merging = MergingListener()

    handler = StreamHandler(stream=sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(ColoredFormatter())
    logger = getLogger(REPORT_LOGGER_NAME)
    logger.setLevel(level)
    logger.addHandler(handler)
    merging.append(LoggingReportingListener.from_logger(logger))

    if report_dir:
        merging.append(HtmlReportingListener.from_path(report_dir))

    return merging
