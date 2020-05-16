"""Matcher compilation."""

from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any, Callable, Dict

import hamcrest
from hamcrest.core.matcher import Matcher as HamcrestMatcher

from preacher.core.hamcrest import after, before
from preacher.core.interpretation.type import require_type
from preacher.core.interpretation.value import (
    Value,
    StaticValue,
    RelativeDatetimeValue,
)
from preacher.core.scenario import (
    Matcher,
    StaticMatcher,
    ValueMatcher,
    RecursiveMatcher,
)
from .error import CompilationError, on_key
from .timedelta import compile_timedelta
from .util import compile_list, map_compile

_STATIC_MATCHER_MAP = {
    # For objects.
    'be_null': StaticMatcher(hamcrest.is_(hamcrest.none())),
    'not_be_null': StaticMatcher(hamcrest.is_(hamcrest.not_none())),

    # For collections.
    'be_empty': StaticMatcher(hamcrest.is_(hamcrest.empty())),

    # Logical.
    'anything': StaticMatcher(hamcrest.is_(hamcrest.anything())),
}

_VALUE_MATCHER_HAMCREST_MAP: Dict[
    str,
    Callable[[object], HamcrestMatcher]
] = {
    # For objects.
    'equal': hamcrest.equal_to,

    # For comparable values.
    'be_greater_than': hamcrest.greater_than,
    'be_greater_than_or_equal_to': hamcrest.greater_than_or_equal_to,
    'be_less_than': hamcrest.less_than,
    'be_less_than_or_equal_to': hamcrest.less_than_or_equal_to,

    # For strings.
    'contain_string': require_type(str, hamcrest.contains_string),
    'start_with': require_type(str, hamcrest.starts_with),
    'end_with': require_type(str, hamcrest.ends_with),
    'match_regexp': require_type(str, hamcrest.matches_regexp),

    # For datetime.
    'be_before': before,
    'be_after': after,
}

_SINGLE_MATCHER_HAMCREST_MAP: Dict[
    str,
    Callable[[HamcrestMatcher], HamcrestMatcher]
] = {
    'be': hamcrest.is_,
    'not': hamcrest.not_,

    # For objects.
    'have_length': hamcrest.has_length,

    # For collections.
    'have_item': hamcrest.has_item,
}

_MULTI_MATCHERS_HAMCREST_MAP: Dict[str, Callable[..., HamcrestMatcher]] = {
    'contain': hamcrest.contains_exactly,
    'contain_exactly': hamcrest.contains_exactly,
    'contain_in_any_order': hamcrest.contains_inanyorder,
    'have_items': hamcrest.has_items,
    'all_of': hamcrest.all_of,
    'any_of': hamcrest.any_of,
}


def _compile_relative_datetime_value(value: object) -> Value[Any]:
    if isinstance(value, datetime):
        if not value.tzinfo:
            value = value.replace(tzinfo=timezone.utc)
        return StaticValue(value)

    delta = compile_timedelta(value)
    return RelativeDatetimeValue(delta)


_VALUE_FACTORY_MAP: Dict[str, Callable[[object], Value[Any]]] = {
    'be_before': _compile_relative_datetime_value,
    'be_after': _compile_relative_datetime_value,
}
_DEFAULT_VALUE_FACTORY: Callable[[object], Value[Any]] = StaticValue


def _compile_taking_single_matcher(key: str, value: object) -> Matcher:
    hamcrest_factory = _SINGLE_MATCHER_HAMCREST_MAP[key]

    if isinstance(value, str) or isinstance(value, Mapping):
        with on_key(key):
            inner = compile(value)
    else:
        inner = ValueMatcher(hamcrest.equal_to, StaticValue(value))

    return RecursiveMatcher(hamcrest_factory, [inner])


def _compile_taking_multi_matchers(key: str, value: object) -> Matcher:
    hamcrest_factory = _MULTI_MATCHERS_HAMCREST_MAP[key]

    with on_key(key):
        value = compile_list(value)
        inner_matchers = list(map_compile(compile, value))

    return RecursiveMatcher(hamcrest_factory, inner_matchers)


def compile(obj: object) -> Matcher:
    if isinstance(obj, str):
        if obj in _STATIC_MATCHER_MAP:
            return _STATIC_MATCHER_MAP[obj]

    if isinstance(obj, Mapping):
        if len(obj) != 1:
            raise CompilationError(
                f'Must have only 1 element, but has {len(obj)}'
            )

        key, value = next(iter(obj.items()))

        if key in _VALUE_MATCHER_HAMCREST_MAP:
            value_factory = _VALUE_FACTORY_MAP.get(key, _DEFAULT_VALUE_FACTORY)
            return ValueMatcher(
                _VALUE_MATCHER_HAMCREST_MAP[key],
                value_factory(value),
            )

        if key in _SINGLE_MATCHER_HAMCREST_MAP:
            return _compile_taking_single_matcher(key, value)

        if key in _MULTI_MATCHERS_HAMCREST_MAP:
            return _compile_taking_multi_matchers(key, value)

    return ValueMatcher(hamcrest.equal_to, StaticValue(obj))
