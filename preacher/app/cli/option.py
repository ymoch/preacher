"""CLI Options."""

import logging
import re
from concurrent.futures import (
    Executor,
    ProcessPoolExecutor,
    ThreadPoolExecutor,
)
from enum import IntEnum
from typing import Callable, Iterable, Mapping, Optional, Tuple, Union

from click import Context, Option, BadParameter, Parameter
from yaml import safe_load
from yaml.error import MarkedYAMLError

from preacher.compilation.argument import Arguments


class Level(IntEnum):
    SKIPPED = logging.DEBUG
    SUCCESS = logging.INFO
    UNSTABLE = logging.WARN
    FAILURE = logging.ERROR

    def __str__(self):
        return self.name.lower()


_LEVEL_MAP: Mapping[str, Level] = {str(level): level for level in Level}
_CONCURRENT_EXECUTOR_FACTORY_MAP: Mapping[str, Callable[[int], Executor]] = {
    'process': ProcessPoolExecutor,
    'thread': ThreadPoolExecutor,
}

LEVEL_CHOICES = tuple(_LEVEL_MAP.keys())
CONCURRENT_EXECUTOR_CHOICES = tuple(_CONCURRENT_EXECUTOR_FACTORY_MAP.keys())


def arguments(
    _context: Context,
    _option_or_parameter: Union[Option, Parameter],
    value: Iterable[str],
) -> Arguments:
    return dict(_parse_argument(v) for v in value)


def level(
    _context: Context,
    _option_or_parameter: Union[Option, Parameter],
    value: str,
) -> int:
    return _LEVEL_MAP[value].value


def positive_float(
    _context: Context,
    _option_or_parameter: Union[Option, Parameter],
    value: Optional[float],
) -> Optional[float]:
    if value is None:
        return value

    if value <= 0.0:
        raise BadParameter(f'must be positive, given {value}')
    return value


def executor_factory(
    _context: Context,
    _option_or_parameter: Union[Option, Parameter],
    value: str,
) -> Callable[[int], Executor]:
    return _CONCURRENT_EXECUTOR_FACTORY_MAP[value.lower()]


def _parse_argument(value: str) -> Tuple[str, object]:
    match = re.match(r'^([^=]+)=(.*)$', value)
    if not match:
        raise BadParameter(f'Invalid format argument: {value}')

    key = match.group(1)
    try:
        value = safe_load(match.group(2))
    except MarkedYAMLError as error:
        raise BadParameter(f'Invalid YAML format: {value}\n{error}')

    return key, value
