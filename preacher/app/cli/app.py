"""CLI Application implementation."""

import sys
from concurrent.futures import Executor, ProcessPoolExecutor
from itertools import chain
from logging import DEBUG, INFO, WARNING, ERROR
from logging import Logger, StreamHandler, getLogger
from typing import Callable, Iterable, Iterator, Optional, Sequence

from preacher.compilation.argument import Arguments
from preacher.compilation.scenario import create_scenario_compiler
from preacher.compilation.yaml import load_all, load_all_from_path
from preacher.core.logger import default_logger
from preacher.core.request import Requester
from preacher.core.scenario import ScenarioRunner, CaseRunner
from preacher.core.scheduling import ScenarioScheduler, Listener, MergingListener
from preacher.core.status import Status
from preacher.core.unit import UnitRunner
from preacher.plugin.loader import load_plugins
from preacher.plugin.manager import get_plugin_manager
from preacher.presentation.listener import LoggingReportingListener, HtmlReportingListener
from .logging import ColoredFormatter

__all__ = ['app', 'create_system_logger', 'create_listener', 'create_scheduler', 'load_objs']

_REPORT_LOGGER_NAME = 'preacher.cli.report.logging'


def app(
    paths: Sequence[str] = (),
    base_url: str = '',
    arguments: Optional[Arguments] = None,
    level: Status = Status.SUCCESS,
    report_dir: Optional[str] = None,
    delay: float = 0.1,
    retry: int = 0,
    timeout: Optional[float] = None,
    concurrency: int = 1,
    executor_factory: Callable[[int], Executor] = ProcessPoolExecutor,
    plugins: Iterable[str] = (),
    verbosity: int = 0,
) -> int:
    """
    Preacher CLI application.

    Returns:
        the exit code.
    """

    # Fill default.
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

    plugin_manager = get_plugin_manager()
    try:
        load_plugins(plugin_manager, plugins, logger)
        compiler = create_scenario_compiler(plugin_manager=plugin_manager)
    except Exception as error:
        logger.exception(error)
        return 3

    objs = load_objs(paths, logger)
    scenario_groups = (compiler.compile_flattening(obj, arguments=arguments) for obj in objs)
    scenarios = chain.from_iterable(scenario_groups)

    listener = create_listener(level, report_dir)
    try:
        logger.info('Start running scenarios.')
        with executor_factory(concurrency) as executor:
            scheduler = create_scheduler(
                executor=executor,
                listener=listener,
                base_url=base_url,
                timeout=timeout,
                retry=retry,
                delay=delay,
            )
            status = scheduler.run(scenarios)
    except Exception as error:
        logger.exception(error)
        return 3
    finally:
        logger.info('End running scenarios.')

    if not status.is_succeeded:
        return 1

    return 0


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


def load_objs(paths: Sequence[str], logger: Logger = default_logger) -> Iterator[object]:
    if not paths:
        logger.info('No scenario file is given. Load scenarios from stdin.')
        return load_all(sys.stdin)
    return chain.from_iterable(load_all_from_path(_hook_loading(path, logger)) for path in paths)


def _hook_loading(path: str, logger: Logger) -> str:
    logger.debug('Load: %s', path)
    return path


def create_listener(level: Status, report_dir: Optional[str]) -> Listener:
    merging = MergingListener()

    logging_level = _status_to_logging_level(level)
    handler = StreamHandler(sys.stdout)
    handler.setLevel(logging_level)
    handler.setFormatter(ColoredFormatter())
    logger = getLogger(_REPORT_LOGGER_NAME)
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


def create_scheduler(
    executor: Executor,
    listener: Listener,
    base_url: str,
    timeout: Optional[float],
    retry: int,
    delay: float,
) -> ScenarioScheduler:
    requester = Requester(base_url=base_url, timeout=timeout)
    unit_runner = UnitRunner(requester=requester, retry=retry, delay=delay)
    case_runner = CaseRunner(unit_runner=unit_runner, listener=listener)
    runner = ScenarioRunner(executor=executor, case_runner=case_runner)
    return ScenarioScheduler(runner=runner, listener=listener)
