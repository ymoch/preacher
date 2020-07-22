"""Preacher CLI."""

import logging
import sys
from concurrent.futures import Executor
from itertools import chain
from typing import Iterator, Sequence, Callable

import click
from click import IntRange

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
    LEVEL_CHOICES,
    CONCURRENT_EXECUTOR_CHOICES,
    arguments,
    level,
    executor_factory,
    positive_float,
)

LOGGER = get_logger(__name__, logging.WARNING)
REPORT_LOGGER_NAME = 'preacher-cli.report.logger'


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


@click.command()
@click.argument(
    'paths',
    metavar='path',
    nargs=-1,
    type=click.Path(exists=True),
)
@click.option(
    'base_url',
    '-u',
    '--base-url',
    help='specify the base URL',
    envvar=_ENV_BASE_URL,
    default='',
)
@click.option(
    'arguments',
    '-a',
    '--argument',
    help='scenario arguments in format "NAME=VALUE"',
    envvar=_ENV_ARGUMENT,
    multiple=True,
    callback=arguments,
)
@click.option(
    'level',
    '-l',
    '--level',
    help='show only above or equal to this level',
    type=click.Choice(LEVEL_CHOICES, case_sensitive=False),
    envvar=_ENV_LEVEL,
    default='success',
    callback=level,
)
@click.option(
    'report_dir_path',
    '-R',
    '--report',
    help='set the report directory',
    type=click.Path(file_okay=False, writable=True),
    envvar=_ENV_REPORT,
)
@click.option(
    'retry',
    '-r',
    '--retry',
    help='set the max retry count',
    metavar='num',
    type=IntRange(min=0),
    envvar=_ENV_RETRY,
    default=0,
)
@click.option(
    'delay',
    '-d',
    '--delay',
    help='set the delay between attempts in seconds',
    metavar='sec',
    type=click.FloatRange(min=0.0),
    envvar=_ENV_DELAY,
    default=0.1,
)
@click.option(
    'timeout',
    '-t',
    '--timeout',
    help='set the delay between attempts in seconds',
    metavar='sec',
    type=click.FloatRange(min=0.0),
    envvar=_ENV_TIMEOUT,
    callback=positive_float
)
@click.option(
    'concurrency',
    '-c',
    '--concurrency',
    help='set the concurrency',
    metavar='num',
    type=IntRange(min=1),
    envvar=_ENV_CONCURRENCY,
    default=1,
)
@click.option(
    'executor_factory',
    '--concurrent-executor',
    help='set the concurrent executor',
    type=click.Choice(CONCURRENT_EXECUTOR_CHOICES, case_sensitive=False),
    envvar=_ENV_CONCURRENT_EXECUTOR,
    default='process',
    callback=executor_factory,
)
@click.option(
    'verbosity',
    '-V',
    '--verbose',
    help='make logging more verbose',
    count=True,
)
@click.help_option('-h', '--help')
@click.version_option(_version, '-v', '--version')
def main(
    paths: Sequence[str],
    base_url: str,
    arguments: Arguments,
    level: int,
    report_dir_path: str,
    retry: int,
    delay: float,
    timeout: float,
    concurrency: int,
    executor_factory: Callable[[int], Executor],
    verbosity: int,
):
    """
    Preacher CLI application.
    """

    print('foo')

    logging_level = logging.WARNING
    if verbosity:
        logging_level = logging.INFO
    if verbosity > 1:
        logging_level = logging.DEBUG

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

    if paths:
        objs: Iterator[object] = chain.from_iterable(
            load_all_from_path(path) for path in paths
        )
    else:
        objs = load_all(sys.stdin)

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
        sys.exit(2)
    logger.info("End running scenarios.")

    if not status.is_succeeded:
        sys.exit(1)
