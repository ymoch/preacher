from __future__ import annotations

import glob
import os
import re
from collections.abc import Mapping
from contextlib import contextmanager
from typing import Iterator, TextIO, Union

from yaml import (
    Node,
    MappingNode,
    ScalarNode,
    BaseLoader,
    MarkedYAMLError,
    load as yaml_load,
    load_all as yaml_load_all,
)
from yaml.composer import Composer
from yaml.constructor import SafeConstructor
from yaml.parser import Parser
from yaml.reader import Reader
from yaml.resolver import Resolver
from yaml.scanner import Scanner

from preacher.core.interpretation import RelativeDatetime
from .argument import ArgumentValue
from .datetime import compile_datetime_format, compile_timedelta
from .error import CompilationError, on_key
from .util import compile_str

PathLike = Union[str, os.PathLike]

WILDCARDS_REGEX = re.compile(r'^.*(\*|\?|\[!?.+\]).*$')

_KEY_DELTA = 'delta'
_KEY_FORMAT = 'format'


def _argument(loader: BaseLoader, node: Node) -> ArgumentValue:
    obj = loader.construct_scalar(node)
    with _on_node(node):
        key = compile_str(obj)
    return ArgumentValue(key)


def _relative_datetime(loader: BaseLoader, node: Node) -> RelativeDatetime:
    if isinstance(node, ScalarNode):
        print('scalar', node)
        value = loader.construct_scalar(node)
        with _on_node(node):
            return _compile_relative_datetime({_KEY_DELTA: value})
    elif isinstance(node, MappingNode):
        print('mapping', node)
        obj = loader.construct_mapping(node)
        with _on_node(node):
            return _compile_relative_datetime(obj)
    else:
        print('other', node)
        with _on_node(node):
            raise CompilationError('Invalid relative datetime value format')


def _compile_relative_datetime(obj: Mapping) -> RelativeDatetime:
    with on_key(_KEY_DELTA):
        delta = compile_timedelta(obj.get(_KEY_DELTA))
    with on_key(_KEY_FORMAT):
        fmt = compile_datetime_format(obj.get(_KEY_FORMAT))
    return RelativeDatetime(delta, fmt)


@contextmanager
def _on_node(node: Node) -> Iterator:
    try:
        yield
    except CompilationError as error:
        mark = node.start_mark
        msg = str(error)
        msg += f'\n  on "{mark.name}", line {mark.line + 1}'
        msg += f', column {mark.column + 1}'
        raise CompilationError(msg, cause=error)


class _YamlLoader:

    def __init__(self):
        self._origin = '.'

        class _Ctor(SafeConstructor):
            pass

        _Ctor.add_constructor('!include', self._include)
        _Ctor.add_constructor('!argument', _argument)
        _Ctor.add_constructor('!relative_datetime', _relative_datetime)

        class _MyLoader(Reader, Scanner, Parser, Composer, _Ctor, Resolver):
            def __init__(self, stream):
                Reader.__init__(self, stream)
                Scanner.__init__(self)
                Parser.__init__(self)
                Composer.__init__(self)
                SafeConstructor.__init__(self)

        self._Loader = _MyLoader

    def load(self, stream: TextIO, origin: PathLike = '.') -> object:
        try:
            with self._on_origin(origin):
                return yaml_load(stream, self._Loader)
        except MarkedYAMLError as error:
            raise CompilationError.wrap(error)

    def load_from_path(self, path: PathLike) -> object:
        origin = os.path.dirname(path)
        try:
            with open(path) as stream:
                return self.load(stream, origin)
        except FileNotFoundError as error:
            raise CompilationError.wrap(error)

    def load_all(self, stream: TextIO, origin: PathLike = '.') -> Iterator:
        try:
            with self._on_origin(origin):
                yield from yaml_load_all(stream, self._Loader)
        except MarkedYAMLError as error:
            raise CompilationError.wrap(error)

    def load_all_from_path(self, path: PathLike) -> Iterator:
        origin = os.path.dirname(path)
        try:
            with open(path) as stream:
                yield from self.load_all(stream, origin)
        except FileNotFoundError as error:
            raise CompilationError.wrap(error)

    def _include(self, loader: BaseLoader, node: Node) -> object:
        base = compile_str(loader.construct_scalar(node))

        path = os.path.join(self._origin, base)
        if WILDCARDS_REGEX.match(path):
            paths = glob.iglob(path, recursive=True)
            return [load_from_path(p) for p in paths]
        return load_from_path(path)

    @contextmanager
    def _on_origin(self, origin: PathLike) -> Iterator:
        original = self._origin
        self._origin = origin
        try:
            yield
        finally:
            self._origin = original


def load(stream: TextIO, origin: PathLike = '.') -> object:
    return _YamlLoader().load(stream, origin)


def load_from_path(path: PathLike) -> object:
    return _YamlLoader().load_from_path(path)


def load_all(stream: TextIO, origin: PathLike = '.') -> Iterator:
    return _YamlLoader().load_all(stream, origin)


def load_all_from_path(path: PathLike) -> Iterator:
    return _YamlLoader().load_all_from_path(path)
