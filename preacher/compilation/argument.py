from collections.abc import Mapping
from typing import Optional

from .util.functional import run_recursively

Arguments = Mapping


class Argument:
    def __init__(self, key: str):
        self._key = key

    @property
    def key(self) -> str:
        return self._key

    def apply_arguments(self, arguments: Optional[Arguments] = None) -> object:
        arguments = arguments or {}
        return arguments.get(self._key)


def _inject_arguments(obj: object, arguments: Optional[Arguments]) -> object:
    if isinstance(obj, Argument):
        return obj.apply_arguments(arguments)
    return obj


def inject_arguments(
    obj: object,
    arguments: Optional[Arguments] = None,
) -> object:
    return run_recursively(lambda o: _inject_arguments(o, arguments), obj)
