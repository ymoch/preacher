import sys
from concurrent.futures import Executor
from itertools import chain
from logging import DEBUG, INFO, WARNING, Logger
from typing import Sequence, Optional, Callable, Iterator

from preacher.compilation.argument import Arguments
from preacher.compilation.scenario import create_scenario_compiler
from preacher.compilation.yaml import load_all, load_all_from_path
from preacher.core.scenario import ScenarioRunner, Listener, MergingListener
from preacher.presentation.listener import (
    LoggingReportingListener,
    HtmlReportingListener,
)
from .logging import get_logger

REPORT_LOGGER_NAME = 'preacher-cli.report.logger'


def app(
    paths: Sequence[str],
    base_url: str,
    arguments: Arguments,
    level: int,
    report_dir_path: Optional[str],
    retry: int,
    delay: float,
    timeout: Optional[float],
    concurrency: int,
    executor_factory: Callable[[int], Executor],
    verbosity: int,
):
    logging_level = _select_level(verbosity)
    logger = get_logger(__name__, logging_level)

    logger.info('Paths: %s', paths)
    logger.info('Arguments: %s', arguments)
    logger.info('Base URL: %s', base_url)
    logger.info('Logging Level: %d', level)
    logger.info('Reporting directory path: %s', report_dir_path)
    logger.info('Max retry count: %d', retry)
    logger.info('Delay between attempts in seconds: %s', delay)
    logger.info('Timeout in seconds: %s', timeout)
    logger.info('Concurrency: %s', concurrency)
    logger.info('Executor: %s', executor_factory)
    logger.info("Verbosity: %d", verbosity)

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
    listener = _create_listener(level, report_dir_path)
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

    logger = get_logger(REPORT_LOGGER_NAME, level)
    merging.append(LoggingReportingListener.from_logger(logger))

    if report_dir:
        merging.append(HtmlReportingListener.from_path(report_dir))

    return merging
