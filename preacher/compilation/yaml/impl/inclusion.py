import glob
import os
import re

from yaml import Node
from yaml.constructor import BaseConstructor

from preacher.compilation.util.type import ensure_str
from preacher.compilation.yaml.loader import Loader, Tag

_WILDCARDS_REGEX = re.compile(r'^.*(\*|\?|\[!?.+]).*$')


class InclusionTag(Tag):

    def construct(
        self,
        loader: Loader,
        constructor: BaseConstructor,
        node: Node,
        origin: str = '.',
    ) -> object:
        # HACK fix typing.
        obj = constructor.construct_scalar(node)  # type: ignore

        base = ensure_str(obj)
        path = os.path.join(origin, base)
        if _WILDCARDS_REGEX.match(path):
            paths = glob.iglob(path, recursive=True)
            return [loader.load_from_path(p) for p in paths]
        return loader.load_from_path(path)
