"""Preacher CLI."""

import sys
from typing import Iterable, Optional, Sequence

from click import FloatRange
from click import IntRange
from click import Path
from click import argument
from click import command
from click import help_option
from click import option
from click import version_option

from preacher import __version__ as _version
from preacher.compilation.argument import Arguments
from preacher.core.status import Status
from .app import app
from .executor import ExecutorFactory
from .option import ArgumentType
from .option import ExecutorFactoryType
from .option import LevelType
from .option import pairs_callback
from .option import positive_float_callback

_ENV_PREFIX = "PREACHER_CLI_"
_ENV_BASE_URL = f"{_ENV_PREFIX}BASE_URL"
_ENV_ARGUMENT = f"{_ENV_PREFIX}ARGUMENT"
_ENV_LEVEL = f"{_ENV_PREFIX}LEVEL"
_ENV_RETRY = f"{_ENV_PREFIX}RETRY"
_ENV_DELAY = f"{_ENV_PREFIX}DELAY"
_ENV_TIMEOUT = f"{_ENV_PREFIX}TIMEOUT"
_ENV_CONCURRENCY = f"{_ENV_PREFIX}CONCURRENCY"
_ENV_CONCURRENT_EXECUTOR = f"{_ENV_PREFIX}CONCURRENT_EXECUTOR"
_ENV_REPORT = f"{_ENV_PREFIX}REPORT"
_ENV_PLUGIN = f"{_ENV_PREFIX}PLUGIN"


@command()
@argument("paths", metavar="path", nargs=-1, type=Path(exists=True))
@option(
    "base_url",
    "-u",
    "--base-url",
    help="specify the base URL",
    envvar=_ENV_BASE_URL,
    default="",
)
@option(
    "arguments",
    "-a",
    "--argument",
    help='scenario arguments in format "NAME=VALUE"',
    type=ArgumentType(),
    envvar=_ENV_ARGUMENT,
    multiple=True,
    callback=pairs_callback,
)
@option(
    "level",
    "-l",
    "--level",
    help="show only above or equal to this level",
    type=LevelType(),
    envvar=_ENV_LEVEL,
    default="success",
)
@option(
    "report_dir",
    "-R",
    "--report",
    help="set the report directory",
    type=Path(file_okay=False, writable=True),
    envvar=_ENV_REPORT,
)
@option(
    "retry",
    "-r",
    "--retry",
    help="set the max retry count",
    metavar="num",
    type=IntRange(min=0),
    envvar=_ENV_RETRY,
    default=0,
)
@option(
    "delay",
    "-d",
    "--delay",
    help="set the delay between attempts in seconds",
    metavar="sec",
    type=FloatRange(min=0.0),
    envvar=_ENV_DELAY,
    default=0.1,
)
@option(
    "timeout",
    "-t",
    "--timeout",
    help="set the delay between attempts in seconds",
    metavar="sec",
    type=FloatRange(min=0.0),
    envvar=_ENV_TIMEOUT,
    callback=positive_float_callback,
)
@option(
    "concurrency",
    "-c",
    "--concurrency",
    help="set the concurrency",
    metavar="num",
    type=IntRange(min=1),
    envvar=_ENV_CONCURRENCY,
    default=1,
)
@option(
    "executor_factory",
    "-E",
    "--executor",
    help="set the concurrent executor",
    type=ExecutorFactoryType(),
    envvar=_ENV_CONCURRENT_EXECUTOR,
    default="process",
)
@option(
    "plugins",
    "-p",
    "--plugin",
    help="add a plugin",
    metavar="path",
    type=Path(exists=True),
    multiple=True,
    envvar=_ENV_PLUGIN,
)
@option(
    "verbosity",
    "-v",
    "--verbose",
    help="make logging more verbose",
    count=True,
)
@help_option("-h", "--help")
@version_option(_version)
def main(
    paths: Sequence[str],
    base_url: str,
    arguments: Arguments,
    level: Status,
    report_dir: Optional[str],
    retry: int,
    delay: float,
    timeout: Optional[float],
    concurrency: int,
    executor_factory: ExecutorFactory,
    plugins: Iterable[str],
    verbosity: int,
) -> None:
    """Preacher CLI: Web API Verification without Coding"""
    exit_code = app(
        paths=paths,
        base_url=base_url,
        arguments=arguments,
        level=level,
        report_dir=report_dir,
        retry=retry,
        delay=delay,
        timeout=timeout,
        concurrency=concurrency,
        executor_factory=executor_factory,
        plugins=plugins,
        verbosity=verbosity,
    )
    sys.exit(exit_code)
