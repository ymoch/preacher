from yaml import BaseLoader, Node

from preacher.compilation.argument import ArgumentValue
from preacher.compilation.type import compile_str
from .error import on_node


def construct_argument(loader: BaseLoader, node: Node) -> ArgumentValue:
    obj = loader.construct_scalar(node)
    with on_node(node):
        key = compile_str(obj)
    return ArgumentValue(key)
