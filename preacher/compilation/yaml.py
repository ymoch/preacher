from __future__ import annotations

import os
from typing import Union, TextIO

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

        path = os.path.join(origin, obj)
        with open(path) as f:
            return _load(yaml, f, os.path.dirname(path))

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


def _resolve(yaml: YAML, obj: object, origin: PathLike) -> object:
    if isinstance(obj, _Inclusion):
        return obj.resolve(origin, yaml)

    if isinstance(obj, _ArgumentValue):
        return obj.resolve()

    return obj


def _load(yaml: YAML, io: TextIO, origin: PathLike) -> object:
    try:
        obj = yaml.load(io)
    except MarkedYAMLError as error:
        raise CompilationError(message=str(error), cause=error)

    return run_recursively(lambda o: _resolve(yaml, o, origin), obj)


def load(io: TextIO, origin: PathLike = '.') -> object:
    yaml = YAML(typ='safe', pure=True)
    yaml.register_class(_Inclusion)
    yaml.register_class(_ArgumentValue)
    return _load(yaml, io, origin)


def load_from_path(path: PathLike) -> object:
    origin = os.path.dirname(path)
    with open(path) as f:
        return load(f, origin)
