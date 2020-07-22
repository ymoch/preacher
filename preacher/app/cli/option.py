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

from click import Context, Option, BadParameter, Parameter, ParamType, Choice
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


class LevelType(ParamType):

    _choice = Choice(tuple(_LEVEL_MAP.keys()), case_sensitive=False)

    def get_metavar(self, param):
        return self._choice.get_metavar(param)

    def get_missing_message(self, param):
        return self._choice.get_missing_message(param)

    def convert(self, value, param, ctx):
        key = self._choice.convert(value, param, ctx)
        return _LEVEL_MAP[key.lower()].value


class ExecutorFactoryType(ParamType):

    _choice = Choice(
        tuple(_CONCURRENT_EXECUTOR_FACTORY_MAP.keys()),
        case_sensitive=False,
    )

    def get_metavar(self, param):
        return self._choice.get_metavar(param)

    def get_missing_message(self, param):
        return self._choice.get_missing_message(param)

    def convert(self, value, param, ctx):
        key = self._choice.convert(value, param, ctx)
        return _CONCURRENT_EXECUTOR_FACTORY_MAP[key.lower()]


def arguments_callback(
    _context: Context,
    _option_or_parameter: Union[Option, Parameter],
    value: Iterable[str],
) -> Arguments:
    return dict(_parse_argument(v) for v in value)


def positive_float_callback(
    _context: Context,
    _option_or_parameter: Union[Option, Parameter],
    value: Optional[float],
) -> Optional[float]:
    if value is None:
        return value

    if value <= 0.0:
        raise BadParameter(f'must be positive, given {value}')
    return value


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
