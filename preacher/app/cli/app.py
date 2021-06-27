"""CLI Application implementation."""

from typing import Iterable, Optional, Sequence

from preacher.compilation.argument import Arguments
from preacher.compilation.scenario import compile_scenarios
from preacher.compilation.yaml import load_from_paths
from preacher.core.scheduling import create_scheduler
from preacher.core.status import Status
from preacher.plugin.loader import load_plugins
from preacher.plugin.manager import get_plugin_manager
from preacher.presentation.listener import create_listener
from .executor import ExecutorFactory, PROCESS_POOL_FACTORY
from .logging import ColoredFormatter, create_system_logger

__all__ = ["app"]

_REPORT_LOGGER_NAME = "preacher.cli.report.logging"


def app(
    paths: Sequence[str] = (),
    base_url: str = "",
    arguments: Optional[Arguments] = None,
    level: Status = Status.SUCCESS,
    report_dir: Optional[str] = None,
    delay: float = 0.1,
    retry: int = 0,
    timeout: Optional[float] = None,
    concurrency: int = 1,
    executor_factory: Optional[ExecutorFactory] = None,
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
        "Running condition\n"
        "  Paths: %s\n"
        "  Arguments: %s\n"
        "  Base URL: %s\n"
        "  Logging report level: %s\n"
        "  Reporting directory path: %s\n"
        "  Max retry count: %d\n"
        "  Delay between attempts in seconds: %s\n"
        "  Timeout in seconds: %s\n"
        "  Concurrency: %s\n"
        "  Executor: %s\n"
        "  Verbosity: %d",
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
        verbosity,
    )

    plugin_manager = get_plugin_manager()
    try:
        load_plugins(plugin_manager, plugins, logger)
    except Exception as error:
        logger.exception(error)
        return 3

    objs = load_from_paths(paths, plugin_manager=plugin_manager, logger=logger)
    scenarios = compile_scenarios(
        objs,
        arguments=arguments,
        plugin_manager=plugin_manager,
        logger=logger,
    )

    listener = create_listener(level=level, formatter=ColoredFormatter(), report_dir=report_dir)
    executor_factory = executor_factory or PROCESS_POOL_FACTORY
    try:
        logger.info("Start running scenarios.")
        with executor_factory.create(concurrency) as executor:
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
        logger.info("End running scenarios.")

    if not status.is_succeeded:
        return 1

    return 0
