"""Preacher CLI."""

import sys
from concurrent.futures import Executor
from itertools import chain
from logging import Logger, WARNING, INFO, DEBUG
from typing import Iterator, Sequence, Callable, Optional

from click import (
    IntRange,
    FloatRange,
    Path,
    command,
    argument,
    option,
    help_option,
    version_option
)

from preacher import __version__ as _version
from preacher.compilation.argument import Arguments
from preacher.compilation.scenario import create_scenario_compiler
from preacher.compilation.yaml import load_all, load_all_from_path
from preacher.core.scenario import ScenarioRunner, MergingListener
from preacher.presentation.listener import (
    HtmlReportingListener,
    LoggingReportingListener,
)
from .logging import get_logger
from .option import (
    ArgumentType,
    LevelType,
    ExecutorFactoryType,
    pairs_callback,
    positive_float_callback,
)

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

    listener = MergingListener()
    listener.append(LoggingReportingListener.from_logger(
        get_logger(REPORT_LOGGER_NAME, level)
    ))
    if report_dir_path:
        listener.append(HtmlReportingListener.from_path(report_dir_path))

    runner = ScenarioRunner(
        base_url=base_url,
        retry=retry,
        delay=delay,
        timeout=timeout
    )
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


_ENV_PREFIX = 'PREACHER_CLI_'
_ENV_BASE_URL = f'{_ENV_PREFIX}BASE_URL'
_ENV_ARGUMENT = f'{_ENV_PREFIX}ARGUMENT'
_ENV_LEVEL = f'{_ENV_PREFIX}LEVEL'
_ENV_RETRY = f'{_ENV_PREFIX}RETRY'
_ENV_DELAY = f'{_ENV_PREFIX}DELAY'
_ENV_TIMEOUT = f'{_ENV_PREFIX}TIMEOUT'
_ENV_CONCURRENCY = f'{_ENV_PREFIX}CONCURRENCY'
_ENV_CONCURRENT_EXECUTOR = f'{_ENV_PREFIX}CONCURRENT_EXECUTOR'
_ENV_REPORT = f'{_ENV_PREFIX}REPORT'


@command()
@argument(
    'paths',
    metavar='path',
    nargs=-1,
    type=Path(exists=True),
)
@option(
    'base_url',
    '-u',
    '--base-url',
    help='specify the base URL',
    envvar=_ENV_BASE_URL,
    default='',
)
@option(
    'arguments',
    '-a',
    '--argument',
    help='scenario arguments in format "NAME=VALUE"',
    type=ArgumentType(),
    envvar=_ENV_ARGUMENT,
    multiple=True,
    callback=pairs_callback,
)
@option(
    'level',
    '-l',
    '--level',
    help='show only above or equal to this level',
    type=LevelType(),
    envvar=_ENV_LEVEL,
    default='success',
)
@option(
    'report_dir_path',
    '-R',
    '--report',
    help='set the report directory',
    type=Path(file_okay=False, writable=True),
    envvar=_ENV_REPORT,
)
@option(
    'retry',
    '-r',
    '--retry',
    help='set the max retry count',
    metavar='num',
    type=IntRange(min=0),
    envvar=_ENV_RETRY,
    default=0,
)
@option(
    'delay',
    '-d',
    '--delay',
    help='set the delay between attempts in seconds',
    metavar='sec',
    type=FloatRange(min=0.0),
    envvar=_ENV_DELAY,
    default=0.1,
)
@option(
    'timeout',
    '-t',
    '--timeout',
    help='set the delay between attempts in seconds',
    metavar='sec',
    type=FloatRange(min=0.0),
    envvar=_ENV_TIMEOUT,
    callback=positive_float_callback,
)
@option(
    'concurrency',
    '-c',
    '--concurrency',
    help='set the concurrency',
    metavar='num',
    type=IntRange(min=1),
    envvar=_ENV_CONCURRENCY,
    default=1,
)
@option(
    'executor_factory',
    '-E',
    '--executor',
    help='set the concurrent executor',
    type=ExecutorFactoryType(),
    envvar=_ENV_CONCURRENT_EXECUTOR,
    default='process',
)
@option(
    'verbosity',
    '-V',
    '--verbose',
    help='make logging more verbose',
    count=True,
)
@help_option('-h', '--help')
@version_option(_version, '-v', '--version')
def main(
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
) -> None:
    """Preacher CLI: Web API Verification without Coding"""
    return app(
        paths=paths,
        base_url=base_url,
        arguments=arguments,
        level=level,
        report_dir_path=report_dir_path,
        retry=retry,
        delay=delay,
        timeout=timeout,
        concurrency=concurrency,
        executor_factory=executor_factory,
        verbosity=verbosity,
    )
