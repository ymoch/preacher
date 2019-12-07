"""Matcher compilation."""

from collections.abc import Mapping
from typing import Any

import hamcrest

from preacher.core.matcher import (
    Matcher,
    StaticMatcher,
    ValueMatcher,
    RecursiveMatcher,
)
from preacher.interpretation import identify
from preacher.interpretation.datetime import interpret_datetime
from preacher.interpretation.value import value_of
from .error import CompilationError, NamedNode
from .util import map_on_key, run_on_key


_STATIC_MATCHER_MAP = {
    # For objects.
    'be_null': StaticMatcher(hamcrest.is_(hamcrest.none())),
    'not_be_null': StaticMatcher(hamcrest.is_(hamcrest.not_none())),

    # For collections.
    'be_empty': StaticMatcher(hamcrest.is_(hamcrest.empty())),

    # Logical.
    'anything': StaticMatcher(hamcrest.is_(hamcrest.anything())),
}

_MATCHER_FUNCTION_MAP_TAKING_SINGLE_VALUE = {
    # For objects.
    'equal': hamcrest.equal_to,
    'have_length': hamcrest.has_length,

    # For comparables.
    'be_greater_than': hamcrest.greater_than,
    'be_greater_than_or_equal_to': hamcrest.greater_than_or_equal_to,
    'be_less_than': hamcrest.less_than,
    'be_less_than_or_equal_to': hamcrest.less_than_or_equal_to,

    # For strings.
    'contain_string': hamcrest.contains_string,
    'start_with': hamcrest.starts_with,
    'end_with': hamcrest.ends_with,
    'match_regexp': hamcrest.matches_regexp,

    # For datetime.
    'be_before': hamcrest.less_than,
    'be_after': hamcrest.greater_than,
}

_MATCHER_FUNCTION_MAP_TAKING_SINGLE_MATCHER = {
    'be': hamcrest.is_,
    'not': hamcrest.not_,
    'have_item': hamcrest.has_item,
}

_MATCHER_FUNCTION_MAP_TAKING_MULTI_MATCHERS = {
    'contain': hamcrest.contains,
    'contain_in_any_order': hamcrest.contains_inanyorder,
    'have_items': hamcrest.has_items,
    'all_of': hamcrest.all_of,
    'any_of': hamcrest.any_of,
}

_INTERPRETER_MAP = {
    'be_before': interpret_datetime,
    'be_after': interpret_datetime,
}


def _compile_taking_single_matcher(key: str, value: Any) -> Matcher:
    hamcrest_factory = _MATCHER_FUNCTION_MAP_TAKING_SINGLE_MATCHER[key]

    if isinstance(value, str) or isinstance(value, Mapping):
        inner = run_on_key(key, compile, value)
    else:
        inner = ValueMatcher(hamcrest.equal_to, value_of(value))

    return RecursiveMatcher(hamcrest_factory, [inner])


def _compile_taking_multi_matchers(key: str, value: Any) -> Matcher:
    hamcrest_factory = _MATCHER_FUNCTION_MAP_TAKING_MULTI_MATCHERS[key]

    if not isinstance(value, list):
        raise CompilationError('Must be a string', path=[NamedNode(key)])

    inner_matchers = list(map_on_key(key, compile, value))
    return RecursiveMatcher(hamcrest_factory, inner_matchers)


def compile(obj: Any) -> Matcher:
    if isinstance(obj, str):
        if obj in _STATIC_MATCHER_MAP:
            return _STATIC_MATCHER_MAP[obj]

    if isinstance(obj, Mapping):
        if len(obj) != 1:
            raise CompilationError(
                f'Must have only 1 element, but has {len(obj)}'
            )

        key, value = next(iter(obj.items()))

        if key in _MATCHER_FUNCTION_MAP_TAKING_SINGLE_VALUE:
            interpret = _INTERPRETER_MAP.get(key, identify)
            return ValueMatcher(
                _MATCHER_FUNCTION_MAP_TAKING_SINGLE_VALUE[key],
                value_of(value),
                interpret=interpret,
            )

        if key in _MATCHER_FUNCTION_MAP_TAKING_SINGLE_MATCHER:
            return _compile_taking_single_matcher(key, value)

        if key in _MATCHER_FUNCTION_MAP_TAKING_MULTI_MATCHERS:
            return _compile_taking_multi_matchers(key, value)

    return ValueMatcher(hamcrest.equal_to, value_of(obj))
