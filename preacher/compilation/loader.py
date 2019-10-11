from __future__ import annotations

import os
from collections.abc import Mapping

from ruamel.yaml import YAML


class _Inclusion:
    yaml_tag = '!include'

    def __init__(self, path: os.PathLike):
        self._path = path

    def resolve(self, base_path: os.PathLike) -> Any:
        #path = os.path.join(os.path.dirname(base_path), self._path)
        #with open(path) as f:
        #    data = yaml.safe_load(f)
        print('Resolved!')
        return {}

    @classmethod
    def from_yaml(cls, constructor, node) -> _Inclusion:
        path = node
        return _Inclusion(path)


def _resolve(obj: Any, path: os.PathLike, yaml: YAML):
    if isinstance(obj, Mapping):
        return {k: _resolve(v, path, yaml) for (k, v) in obj.items()}

    if isinstance(obj, list):
        return [_resolve(item, path, yaml) for item in obj]

    if isinstance(obj, _Inclusion):
        return obj.resolve(path)

    return obj


def load_yaml(path: str):
    yaml = YAML()
    yaml.register_class(_Inclusion)
    with open(path) as f:
        return _resolve(yaml.load(f), path, yaml)
