from __future__ import annotations

import glob
import os
import re
from contextlib import contextmanager
from datetime import timedelta
from typing import Iterator, Optional, TextIO, Union

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

from preacher.compilation.argument import ArgumentValue
from preacher.compilation.datetime import compile_datetime_format, compile_timedelta
from preacher.compilation.error import CompilationError
from preacher.compilation.util import compile_str
from preacher.core.datetime import DatetimeFormat
from preacher.core.interpretation import RelativeDatetime
from preacher.yaml import load_from_path

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
        return _relative_datetime_of_scalar(loader, node)
    elif isinstance(node, MappingNode):
        return _relative_datetime_of_mapping(loader, node)
    else:
        with _on_node(node):
            raise CompilationError('Invalid relative datetime value format')


def _relative_datetime_of_scalar(
    loader: BaseLoader,
    node: ScalarNode,
) -> RelativeDatetime:
    obj = loader.construct_scalar(node)
    with _on_node(node):
        delta = compile_timedelta(obj)
    return RelativeDatetime(delta)


def _relative_datetime_of_mapping(
    loader: BaseLoader,
    node: MappingNode,
) -> RelativeDatetime:
    delta: Optional[timedelta] = None
    format: Optional[DatetimeFormat] = None

    for key_node, value_node in node.value:
        if key_node.value == _KEY_DELTA:
            obj = loader.construct_scalar(value_node)
            with _on_node(value_node):
                delta = compile_timedelta(obj)
            continue
        if key_node.value == _KEY_FORMAT:
            obj = loader.construct_scalar(value_node)
            with _on_node(node):
                format = compile_datetime_format(obj)
            continue

    return RelativeDatetime(delta, format)


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


class Loader:

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
