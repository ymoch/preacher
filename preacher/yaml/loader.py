from __future__ import annotations

import glob
import os
import re
from contextlib import contextmanager
from typing import Iterator, TextIO, Union

from yaml import Node, BaseLoader, MarkedYAMLError, load, load_all
from yaml.composer import Composer
from yaml.constructor import SafeConstructor
from yaml.parser import Parser
from yaml.reader import Reader
from yaml.resolver import Resolver
from yaml.scanner import Scanner

from preacher.compilation.util import compile_str
from .argument import construct_argument
from .datetime import construct_relative_datetime
from .error import YamlError, on_node

PathLike = Union[str, os.PathLike]

WILDCARDS_REGEX = re.compile(r'^.*(\*|\?|\[!?.+\]).*$')


class Loader:

    def __init__(self):
        self._origin = '.'

        class _Ctor(SafeConstructor):
            pass

        _Ctor.add_constructor('!include', self._include)
        _Ctor.add_constructor('!argument', construct_argument)
        _Ctor.add_constructor(
            '!relative_datetime',
            construct_relative_datetime,
        )

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
                return load(stream, self._Loader)
        except MarkedYAMLError as error:
            raise YamlError(cause=error)

    def load_from_path(self, path: PathLike) -> object:
        origin = os.path.dirname(path)
        try:
            with open(path) as stream:
                return self.load(stream, origin)
        except FileNotFoundError as error:
            raise YamlError(cause=error)

    def load_all(self, stream: TextIO, origin: PathLike = '.') -> Iterator:
        try:
            with self._on_origin(origin):
                yield from load_all(stream, self._Loader)
        except MarkedYAMLError as error:
            raise YamlError(cause=error)

    def load_all_from_path(self, path: PathLike) -> Iterator:
        origin = os.path.dirname(path)
        try:
            with open(path) as stream:
                yield from self.load_all(stream, origin)
        except FileNotFoundError as error:
            raise YamlError(cause=error)

    def _include(self, loader: BaseLoader, node: Node) -> object:
        obj = loader.construct_scalar(node)

        with on_node(node):
            base = compile_str(obj)
            path = os.path.join(self._origin, base)
            if WILDCARDS_REGEX.match(path):
                paths = glob.iglob(path, recursive=True)
                return [self.load_from_path(p) for p in paths]
            return self.load_from_path(path)

    @contextmanager
    def _on_origin(self, origin: PathLike) -> Iterator:
        original = self._origin
        self._origin = origin
        try:
            yield
        finally:
            self._origin = original
