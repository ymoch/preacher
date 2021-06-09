from yaml import Node
from yaml.constructor import BaseConstructor

from preacher.compilation.argument import Argument
from preacher.compilation.util.type import ensure_str
from preacher.compilation.yaml.loader import Loader, Tag


class ArgumentTag(Tag):

    def construct(
        self,
        loader: Loader,
        constructor: BaseConstructor,
        node: Node,
        origin: str = '.',
    ) -> object:
        # HACK fix typing.
        obj = constructor.construct_scalar(node)  # type: ignore
        key = ensure_str(obj)
        return Argument(key)
