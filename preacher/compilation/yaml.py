from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Any, Optional, Union

from ruamel.yaml import YAML

PathLike = Union[str, os.PathLike]


class _Inclusion:
    yaml_tag = '!include'

    def __init__(self, path: PathLike):
        self._path = path

    def resolve(self, origin: PathLike, yaml: YAML) -> Optional[Any]:
        path = os.path.join(os.path.dirname(origin), self._path)
        return _load(path, yaml)

    @classmethod
    def from_yaml(cls, constructor, node) -> _Inclusion:
        path = node.value
        return _Inclusion(path)


def _resolve(obj: Any, origin: PathLike, yaml: YAML) -> Optional[Any]:
    if isinstance(obj, Mapping):
        return {k: _resolve(v, origin, yaml) for (k, v) in obj.items()}

    if isinstance(obj, list):
        return [_resolve(item, origin, yaml) for item in obj]

    if isinstance(obj, _Inclusion):
        return obj.resolve(origin, yaml)

    return obj


def _load(path: PathLike, yaml: YAML) -> Optional[Any]:
    with open(path) as f:
        return _resolve(yaml.load(f), path, yaml)


def load(path: PathLike) -> Optional[Any]:
    yaml = YAML(typ='safe', pure=True)
    yaml.register_class(_Inclusion)
    return _load(path, yaml)
