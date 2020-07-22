"""Preacher CLI."""

from concurrent.futures import Executor
from typing import Sequence, Callable, Optional

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
from .app import app
from .option import (
    ArgumentType,
    LevelType,
    ExecutorFactoryType,
    pairs_callback,
    positive_float_callback,
)

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
