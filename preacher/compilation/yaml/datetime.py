from datetime import timedelta
from typing import Optional

from yaml import BaseLoader, MappingNode, ScalarNode, Node

from preacher.compilation.datetime import compile_timedelta, compile_datetime_format
from preacher.core.datetime import DatetimeFormat
from preacher.core.value import RelativeDatetime
from .error import YamlError, on_node

_KEY_DELTA = 'delta'
_KEY_FORMAT = 'format'


def construct_relative_datetime(loader: BaseLoader, node: Node) -> RelativeDatetime:
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
) -> RelativeDatetime:
    obj = loader.construct_scalar(node)
    with on_node(node):
        delta = compile_timedelta(obj)
    return RelativeDatetime(delta)


def _construct_relative_datetime_of_mapping(
    loader: BaseLoader,
    node: MappingNode,
) -> RelativeDatetime:
    delta: Optional[timedelta] = None
    format: Optional[DatetimeFormat] = None

    for key_node, value_node in node.value:
        if key_node.value == _KEY_DELTA:
            obj = loader.construct_scalar(value_node)
            with on_node(value_node):
                delta = compile_timedelta(obj)
            continue
        if key_node.value == _KEY_FORMAT:
            obj = loader.construct_scalar(value_node)
            with on_node(node):
                format = compile_datetime_format(obj)
            continue

    return RelativeDatetime(delta, format)
