from typing import Mapping as MappingType, Optional

from preacher.compilation.util import run_recursively

Arguments = MappingType[str, object]


class Argument:

    def __init__(self, key: str):
        self._key = key

    @property
    def key(self) -> str:
        return self._key

    def apply_arguments(self, arguments: Optional[Arguments] = None) -> object:
        arguments = arguments or {}
        return arguments.get(self._key, arguments or {})


def _resolve_arguments(obj: object, arguments: Optional[Arguments]) -> object:
    if isinstance(obj, Argument):
        return obj.apply_arguments(arguments)
    return obj


def resolve_arguments(
    obj: object,
    arguments: Optional[Arguments] = None,
) -> object:
    return run_recursively(lambda o: _resolve_arguments(o, arguments), obj)
