import sys
from concurrent.futures import Executor, ProcessPoolExecutor
from itertools import chain
from logging import DEBUG, INFO, WARNING, ERROR
from logging import Logger, StreamHandler, getLogger
from typing import Sequence, Optional, Callable, Iterator

from preacher.compilation.argument import Arguments
from preacher.compilation.scenario import create_scenario_compiler
from preacher.compilation.yaml import load_all, load_all_from_path
from preacher.core.scenario import ScenarioRunner, Listener, MergingListener
from preacher.core.status import Status
from preacher.presentation.listener import (
    LoggingReportingListener,
    HtmlReportingListener,
)
from .logging import ColoredFormatter

REPORT_LOGGER_NAME = 'preacher.cli.report.logging'


def app(
    paths: Optional[Sequence[str]] = None,
    base_url: str = '',
    arguments: Optional[Arguments] = None,
    level: Status = Status.SUCCESS,
    report_dir: Optional[str] = None,
    delay: float = 0.1,
    retry: int = 0,
    timeout: Optional[float] = None,
    concurrency: int = 1,
    executor_factory: Callable[[int], Executor] = ProcessPoolExecutor,
    verbosity: int = 0,
):
    # Fill default.
    paths = paths or ()
    arguments = arguments or {}

    logger = create_system_logger(verbosity)

    logger.debug(
        'Running condition\n'
        '  Paths: %s\n'
        '  Arguments: %s\n'
        '  Base URL: %s\n'
        '  Logging report level: %s\n'
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

    objs = load_objs(paths, logger=logger)
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
    listener = create_listener(level, report_dir)
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


def create_system_logger(verbosity: int) -> Logger:
    level = _verbosity_to_logging_level(verbosity)
    handler = StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(ColoredFormatter(fmt='[%(levelname)s] %(message)s'))
    logger = getLogger(__name__)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger


def _verbosity_to_logging_level(verbosity: int) -> int:
    if verbosity > 1:
        return DEBUG
    if verbosity > 0:
        return INFO
    return WARNING


def load_objs(paths: Sequence[str], logger: Logger) -> Iterator[object]:
    if not paths:
        logger.info('Load scenarios from stdin.')
        return load_all(sys.stdin)
    return chain.from_iterable(load_all_from_path(path) for path in paths)


def create_listener(level: Status, report_dir: Optional[str]) -> Listener:
    merging = MergingListener()

    logging_level = _status_to_logging_level(level)
    handler = StreamHandler(stream=sys.stdout)
    handler.setLevel(logging_level)
    handler.setFormatter(ColoredFormatter())
    logger = getLogger(REPORT_LOGGER_NAME)
    logger.setLevel(logging_level)
    logger.addHandler(handler)
    merging.append(LoggingReportingListener.from_logger(logger))

    if report_dir:
        merging.append(HtmlReportingListener.from_path(report_dir))

    return merging


def _status_to_logging_level(level: Status) -> int:
    if level is Status.SKIPPED:
        return DEBUG
    if level is Status.SUCCESS:
        return INFO
    if level is Status.UNSTABLE:
        return WARNING
    return ERROR
