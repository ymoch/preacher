from __future__ import annotations

import glob
import os
import re
from typing import Union, TextIO

from yaml import YAMLObject, MarkedYAMLError, Node, load as yaml_load
from yaml.composer import Composer
from yaml.constructor import SafeConstructor
from yaml.parser import Parser
from yaml.reader import Reader
from yaml.resolver import Resolver
from yaml.scanner import Scanner

from preacher.core.interpretation.value import RelativeDatetimeValue
from .argument import ArgumentValue
from .error import CompilationError
from .timedelta import compile_timedelta
from .util import run_recursively

PathLike = Union[str, os.PathLike]

WILDCARDS_REGEX = re.compile(r'^.*(\*|\?|\[!?.+\]).*$')


class _Inclusion(YAMLObject):
    yaml_tag = '!include'

    def __init__(self, obj: object):
        self._obj = obj

    def resolve(self, origin: PathLike) -> object:
        obj = self._obj
        if not isinstance(obj, str):
            raise CompilationError(f'Must be a string, given {type(obj)}')

        path = os.path.join(origin, obj)
        if WILDCARDS_REGEX.match(path):
            paths = glob.iglob(path, recursive=True)
            return [load_from_path(p) for p in paths]
        return load_from_path(path)

    @classmethod
    def from_yaml(cls, loader, node: Node) -> _Inclusion:
        return _Inclusion(node.value)


class _ArgumentValue(YAMLObject):
    yaml_tag = '!argument'

    def __init__(self, obj: object):
        self._obj = obj

    def resolve(self) -> ArgumentValue:
        obj = self._obj
        if not isinstance(obj, str):
            raise CompilationError(f'Must be a key string, given {type(obj)}')
        return ArgumentValue(obj)

    @classmethod
    def from_yaml(cls, loader, node: Node) -> _ArgumentValue:
        return _ArgumentValue(node.value)


class _RelativeDatetime(YAMLObject):
    yaml_tag = '!relative_datetime'

    def __init__(self, obj: object):
        self._obj = obj

    def resolve(self) -> RelativeDatetimeValue:
        obj = self._obj
        if not isinstance(obj, str):
            raise CompilationError(f'Must be a string, given {type(obj)}')

        delta = compile_timedelta(obj)
        return RelativeDatetimeValue(delta)

    @classmethod
    def from_yaml(cls, loader, node: Node) -> _RelativeDatetime:
        return _RelativeDatetime(node.value)


class _CustomSafeConstructor(SafeConstructor):
    pass


_CustomSafeConstructor.add_constructor(
    _Inclusion.yaml_tag,
    _Inclusion.from_yaml,
)
_CustomSafeConstructor.add_constructor(
    _ArgumentValue.yaml_tag,
    _ArgumentValue.from_yaml,
)
_CustomSafeConstructor.add_constructor(
    _RelativeDatetime.yaml_tag,
    _RelativeDatetime.from_yaml,
)


class _CustomSafeLoader(
    Reader,
    Scanner,
    Parser,
    Composer,
    _CustomSafeConstructor,
    Resolver,
):

    def __init__(self, stream):
        Reader.__init__(self, stream)
        Scanner.__init__(self)
        Parser.__init__(self)
        Composer.__init__(self)
        SafeConstructor.__init__(self)


def _resolve(obj: object, origin: PathLike) -> object:
    if isinstance(obj, _Inclusion):
        return obj.resolve(origin)

    if isinstance(obj, _ArgumentValue):
        return obj.resolve()

    if isinstance(obj, _RelativeDatetime):
        return obj.resolve()

    return obj


def load(io: TextIO, origin: PathLike = '.') -> object:
    try:
        obj = yaml_load(io, Loader=_CustomSafeLoader)
    except MarkedYAMLError as error:
        raise CompilationError(message=str(error), cause=error)

    return run_recursively(lambda o: _resolve(o, origin), obj)


def load_from_path(path: PathLike) -> object:
    origin = os.path.dirname(path)
    with open(path) as f:
        return load(f, origin)
