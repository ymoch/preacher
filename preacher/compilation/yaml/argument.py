from yaml import BaseLoader, Node

from preacher.compilation.argument import Argument
from preacher.compilation.util.type import ensure_str
from .error import on_node


def construct_argument(loader: BaseLoader, node: Node) -> Argument:
    obj = loader.construct_scalar(node)
    with on_node(node):
        key = ensure_str(obj)
    return Argument(key)
