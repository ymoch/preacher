from typing import Optional

from yaml import MappingNode, ScalarNode, Node
from yaml.constructor import BaseConstructor

from preacher.compilation.datetime import compile_datetime_format
from preacher.compilation.yaml.loader import Loader, Tag
from preacher.core.datetime import DatetimeFormat, DatetimeWithFormat
from preacher.core.value import Value
from preacher.core.value.impl.datetime import parse_datetime_value_with_format
from preacher.compilation.yaml.error import YamlError, on_node

_KEY_DELTA = 'delta'
_KEY_FORMAT = 'format'


class RelativeDatetimeTag(Tag):

    def construct(
        self,
        loader: Loader,
        constructor: BaseConstructor,
        node: Node,
        origin: str = '.',
    ) -> object:
        return _construct_relative_datetime(constructor, node)


def _construct_relative_datetime(
    constructor: BaseConstructor,
    node: Node,
) -> Value[DatetimeWithFormat]:
    if isinstance(node, ScalarNode):
        return _construct_relative_datetime_of_scalar(constructor, node)
    elif isinstance(node, MappingNode):
        return _construct_relative_datetime_of_mapping(constructor, node)
    else:
        message = 'Invalid relative datetime value format'
        raise YamlError(message, mark=node.start_mark)


def _construct_relative_datetime_of_scalar(
    constructor: BaseConstructor,
    node: ScalarNode,
) -> Value[DatetimeWithFormat]:
    obj = constructor.construct_scalar(node)
    with on_node(node):
        return parse_datetime_value_with_format(obj)


def _construct_relative_datetime_of_mapping(
    constructor: BaseConstructor,
    node: MappingNode,
) -> Value[DatetimeWithFormat]:
    # HACK fix typing.
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
        obj = constructor.construct_scalar(format_node)  # type: ignore
        with on_node(node):
            format = compile_datetime_format(obj)

    if datetime_value_node:
        datetime_value = constructor.construct_scalar(datetime_value_node)  # type: ignore
        with on_node(datetime_value_node):
            return parse_datetime_value_with_format(datetime_value, format)
    return parse_datetime_value_with_format('now', format)
