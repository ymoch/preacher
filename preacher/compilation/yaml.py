from __future__ import annotations

import os
from collections.abc import Mapping
from functools import partial
from typing import Union

from ruamel.yaml import YAML, Node
from ruamel.yaml.constructor import ConstructorError

from preacher.interpretation.value import ArgumentValue
from .error import CompilationError
from .util import map, run_on_key

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


class _Argument:
    yaml_tag = '!argument'

    def __init__(self, obj: object):
        self._obj = obj

    def resolve(self) -> ArgumentValue:
        obj = self._obj
        if not isinstance(obj, str):
            raise CompilationError(f'Must be a key string, given {type(obj)}')
        return ArgumentValue(obj)


def _resolve(obj: object, origin: PathLike, yaml: YAML) -> object:
    resolve = partial(_resolve, origin=origin, yaml=yaml)

    if isinstance(obj, Mapping):
        return {k: run_on_key(k, resolve, v) for (k, v) in obj.items()}

    if isinstance(obj, list):
        return list(map(resolve, obj))

    if isinstance(obj, _Inclusion):
        return obj.resolve(origin, yaml)

    if isinstance(obj, _Argument):
        return obj.resolve()

    return obj


def _load(path: PathLike, yaml: YAML) -> object:
    with open(path) as f:
        try:
            obj = yaml.load(f)
        except ConstructorError as error:
            raise CompilationError(message=str(error), cause=error)

        return _resolve(obj, path, yaml)


def load(path: PathLike) -> object:
    yaml = YAML(typ='safe', pure=True)
    yaml.register_class(_Inclusion)
    return _load(path, yaml)
