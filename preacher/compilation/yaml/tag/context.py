from yaml import Node
from yamlen import Tag, TagContext

from preacher.core.value.impl.context import ContextualValue


class ContextTag(Tag):
    def construct(self, node: Node, context: TagContext) -> ContextualValue:
        key = context.constructor.construct_scalar(node)  # type: ignore
        return ContextualValue(key)
