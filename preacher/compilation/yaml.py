from __future__ import annotations

import os
from typing import Union

from ruamel.yaml import YAML, Node
from ruamel.yaml.error import MarkedYAMLError

from .argument import ArgumentValue
from .error import CompilationError
from .util import run_recursively

PathLike = Union[str, os.PathLike]


class _Inclusion:
    yaml_tag = '!include'

    def __init__(self, obj: object):
        self._obj = obj

    def resolve(self, origin: PathLike, yaml: YAML) -> object:
        obj = self._obj
        if not isinstance(obj, str):
            raise CompilationError(f'Must be a string, given {type(obj)}')

        path = os.path.join(os.path.dirname(origin), obj)
        return _load(path, yaml)

    @classmethod
    def from_yaml(cls, _constructor, node: Node) -> _Inclusion:
        return _Inclusion(node.value)


class _ArgumentValue:
    yaml_tag = '!argument'

    def __init__(self, obj: object):
        self._obj = obj

    def resolve(self) -> ArgumentValue:
        obj = self._obj
        if not isinstance(obj, str):
            raise CompilationError(f'Must be a key string, given {type(obj)}')
        return ArgumentValue(obj)

    @classmethod
    def from_yaml(cls, _constructor, node: Node) -> _ArgumentValue:
        return _ArgumentValue(node.value)


def _resolve(obj: object, origin: PathLike, yaml: YAML) -> object:
    if isinstance(obj, _Inclusion):
        return obj.resolve(origin, yaml)

    if isinstance(obj, _ArgumentValue):
        return obj.resolve()

    return obj


def _load(path: PathLike, yaml: YAML) -> object:
    with open(path) as f:
        try:
            obj = yaml.load(f)
        except MarkedYAMLError as error:
            raise CompilationError(message=str(error), cause=error)

    return run_recursively(lambda o: _resolve(o, origin=path, yaml=yaml), obj)


def load(path: PathLike) -> object:
    yaml = YAML(typ='safe', pure=True)
    yaml.register_class(_Inclusion)
    yaml.register_class(_ArgumentValue)
    return _load(path, yaml)
