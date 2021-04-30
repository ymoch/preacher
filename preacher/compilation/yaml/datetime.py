from typing import Optional

from yaml import BaseLoader, MappingNode, ScalarNode, Node

from preacher.compilation.datetime import compile_datetime_format
from preacher.compilation.value.datetime import compile_datetime_value_with_format
from preacher.core.datetime import DatetimeFormat, DatetimeWithFormat
from preacher.core.value import Value
from .error import YamlError, on_node

_KEY_DELTA = 'delta'
_KEY_FORMAT = 'format'


def construct_relative_datetime(loader: BaseLoader, node: Node) -> Value[DatetimeWithFormat]:
    if isinstance(node, ScalarNode):
        return _construct_relative_datetime_of_scalar(loader, node)
    elif isinstance(node, MappingNode):
        return _construct_relative_datetime_of_mapping(loader, node)
    else:
        message = 'Invalid relative datetime value format'
        raise YamlError(message, mark=node.start_mark)


def _construct_relative_datetime_of_scalar(
    loader: BaseLoader,
    node: ScalarNode,
) -> Value[DatetimeWithFormat]:
    obj = loader.construct_scalar(node)
    with on_node(node):
        return compile_datetime_value_with_format(obj)


def _construct_relative_datetime_of_mapping(
    loader: BaseLoader,
    node: MappingNode,
) -> Value[DatetimeWithFormat]:
    format_node: Optional[Node] = None
    datetime_value_node: Optional[Node] = None
    for key_node, value_node in node.value:
        if key_node.value == _KEY_DELTA:
            datetime_value_node = value_node
            continue
        if key_node.value == _KEY_FORMAT:
            format_node = value_node
            continue

    format: Optional[DatetimeFormat] = None
    if format_node:
        obj = loader.construct_scalar(format_node)
        with on_node(node):
            format = compile_datetime_format(obj)

    if datetime_value_node:
        datetime_value = loader.construct_scalar(datetime_value_node)
        with on_node(datetime_value_node):
            return compile_datetime_value_with_format(datetime_value, format)
    return compile_datetime_value_with_format('now', format)
