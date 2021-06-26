from yaml import Node
from yamlen import Tag, TagContext

from preacher.compilation.argument import Argument


class ArgumentTag(Tag):
    def construct(self, node: Node, context: TagContext) -> object:
        key = context.constructor.construct_scalar(node)  # type: ignore
        return Argument(key)
