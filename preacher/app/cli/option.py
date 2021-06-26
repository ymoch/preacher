"""CLI Options."""

import logging
import re
import shlex
from enum import IntEnum
from typing import Iterable, Mapping, Optional, Tuple, Union, Any

from click import Choice
from click import Context
from click import BadParameter
from click import Parameter
from click import ParamType
from click import Option
from click import STRING

from yaml import safe_load
from yaml.error import MarkedYAMLError

from preacher.compilation.argument import Arguments
from preacher.core.status import Status
from .executor import ExecutorFactory, PROCESS_POOL_FACTORY, THREAD_POOL_FACTORY


class Level(IntEnum):
    SKIPPED = logging.DEBUG
    SUCCESS = logging.INFO
    UNSTABLE = logging.WARN
    FAILURE = logging.ERROR

    def __str__(self):
        return self.name.lower()


_LEVEL_MAP: Mapping[str, Level] = {str(level): level for level in Level}
_CONCURRENT_EXECUTOR_FACTORY_MAP: Mapping[str, ExecutorFactory] = {
    "process": PROCESS_POOL_FACTORY,
    "thread": THREAD_POOL_FACTORY,
}


class ArgumentType(ParamType):

    _base = STRING
    name = _base.name

    def convert(self, value, param, ctx):
        exp = self._base.convert(value, param, ctx)
        return _parse_argument(exp)

    def split_envvar_value(self, rv):
        return shlex.split(rv)


class LevelType(ParamType):

    _choice = Choice(tuple(item.name.lower() for item in Status), case_sensitive=False)
    name = _choice.name

    def get_metavar(self, param: Parameter) -> str:
        return self._choice.get_metavar(param)

    def get_missing_message(self, param: Parameter) -> str:
        return self._choice.get_missing_message(param)

    def convert(self, value: Any, param: Optional[Parameter], ctx: Optional[Context]) -> Status:
        if isinstance(value, Status):
            return value
        key = self._choice.convert(value, param, ctx).lower()
        return next(item for item in Status if item.name.lower() == key)


class ExecutorFactoryType(ParamType):

    _choice = Choice(
        tuple(_CONCURRENT_EXECUTOR_FACTORY_MAP.keys()),
        case_sensitive=False,
    )
    name = _choice.name

    def get_metavar(self, param):
        return self._choice.get_metavar(param)

    def get_missing_message(self, param):
        return self._choice.get_missing_message(param)

    def convert(
        self,
        value: Any,
        param: Optional[Parameter],
        ctx: Optional[Context],
    ) -> ExecutorFactory:
        if isinstance(value, ExecutorFactory):
            return value
        key = self._choice.convert(value, param, ctx)
        return _CONCURRENT_EXECUTOR_FACTORY_MAP[key.lower()]


def pairs_callback(
    _context: Context,
    _option_or_parameter: Union[Option, Parameter],
    value: Iterable[Tuple[str, object]],
) -> Arguments:
    return dict(value)


def positive_float_callback(
    _context: Context,
    _option_or_parameter: Union[Option, Parameter],
    value: Optional[float],
) -> Optional[float]:
    if value is None:
        return value

    if value <= 0.0:
        raise BadParameter(f"must be positive, given {value}")
    return value


def _parse_argument(value: str) -> Tuple[str, object]:
    match = re.match(r"^([^=]+)=(.*)$", value)
    if not match:
        raise BadParameter(f"Invalid format argument: {value}")

    key = match.group(1)
    try:
        value = safe_load(match.group(2))
    except MarkedYAMLError as error:
        raise BadParameter(f"Invalid YAML format: {value}\n{error}")

    return key, value
