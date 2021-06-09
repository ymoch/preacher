"""YAML loaders."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from contextlib import contextmanager
from functools import partial
from typing import Iterator, TextIO

from yaml import Node, MarkedYAMLError
from yaml import load as _load, load_all as _load_all
from yaml.composer import Composer
from yaml.constructor import BaseConstructor, SafeConstructor
from yaml.parser import Parser
from yaml.reader import Reader
from yaml.resolver import Resolver
from yaml.scanner import Scanner

from .error import YamlError, on_node


class Tag(ABC):

    @abstractmethod
    def construct(
        self,
        loader: Loader,
        constructor: BaseConstructor,
        node: Node,
        origin: str = '.',
    ) -> object:
        """Construct a tag."""


class Loader:

    def __init__(self):
        self._origin = '.'

        class _Ctor(SafeConstructor):
            pass

        class _Loader(Reader, Scanner, Parser, Composer, _Ctor, Resolver):
            def __init__(self, stream):
                Reader.__init__(self, stream)
                Scanner.__init__(self)
                Parser.__init__(self)
                Composer.__init__(self)
                SafeConstructor.__init__(self)

        self._ctor = _Ctor
        self._Loader = _Loader

    def add_tag(self, name: str, tag: Tag) -> None:
        self._ctor.add_constructor(name, partial(self._apply_tag, tag))

    def load(self, stream: TextIO, origin: str = '.') -> object:
        try:
            with self._on_origin(origin):
                return _load(stream, self._Loader)
        except MarkedYAMLError as error:
            raise YamlError(cause=error)

    def load_from_path(self, path: str) -> object:
        origin = os.path.dirname(path)
        try:
            with open(path) as stream:
                return self.load(stream, origin)
        except FileNotFoundError as error:
            raise YamlError(cause=error)

    def load_all(self, stream: TextIO, origin: str = '.') -> Iterator:
        try:
            with self._on_origin(origin):
                yield from _load_all(stream, self._Loader)
        except MarkedYAMLError as error:
            raise YamlError(cause=error)

    def load_all_from_path(self, path: str) -> Iterator:
        origin = os.path.dirname(path)
        try:
            with open(path) as stream:
                yield from self.load_all(stream, origin)
        except FileNotFoundError as error:
            raise YamlError(cause=error)

    def _apply_tag(self, tag: Tag, ctor: BaseConstructor, node: Node) -> object:
        with on_node(node):
            return tag.construct(self, ctor, node, origin=self._origin)

    @contextmanager
    def _on_origin(self, origin: str) -> Iterator:
        original = self._origin
        self._origin = origin
        try:
            yield
        finally:
            self._origin = original
