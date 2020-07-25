"""Matcher compilation."""

from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Tuple

import hamcrest

from preacher.compilation.datetime import compile_timedelta
from preacher.compilation.error import CompilationError, on_key
from preacher.compilation.util.functional import map_compile
from preacher.compilation.util.type import ensure_list
from preacher.core.datetime import DatetimeWithFormat
from preacher.core.value import Value, StaticValue, RelativeDatetime
from preacher.core.verification.hamcrest import after, before
from preacher.core.verification.matcher import MatcherFactory
from preacher.core.verification.matcher import MatcherFunc
from preacher.core.verification.matcher import RecursiveMatcherFactory
from preacher.core.verification.matcher import StaticMatcherFactory
from preacher.core.verification.matcher import ValueMatcherFactory
from preacher.core.verification.type import require_type

ValueFunc = Callable[[object], Value]

_STATIC_MATCHER_MAP: Dict[str, MatcherFactory] = {
    # For objects.
    'be_null': StaticMatcherFactory(hamcrest.is_(hamcrest.none())),
    'not_be_null': StaticMatcherFactory(hamcrest.is_(hamcrest.not_none())),

    # For collections.
    'be_empty': StaticMatcherFactory(hamcrest.is_(hamcrest.empty())),

    # Logical.
    'anything': StaticMatcherFactory(hamcrest.is_(hamcrest.anything())),
}

_VALUE_MATCHER_HAMCREST_MAP: Dict[str, MatcherFunc] = {
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

_RECURSIVE_MATCHERS_HAMCREST_MAP: Dict[str, MatcherFunc] = {
    'be': hamcrest.is_,

    # For objects.
    'have_length': hamcrest.has_length,

    # For collections.
    'have_item': hamcrest.has_item,
    'contain': hamcrest.contains_exactly,
    'contain_exactly': hamcrest.contains_exactly,
    'contain_in_any_order': hamcrest.contains_inanyorder,
    'have_items': hamcrest.has_items,

    # Logical.
    'not': hamcrest.not_,
    'all_of': hamcrest.all_of,
    'any_of': hamcrest.any_of,
}


def _compile_datetime_value(value: object) -> Value[DatetimeWithFormat]:
    if isinstance(value, datetime):
        if not value.tzinfo:
            value = value.replace(tzinfo=timezone.utc)
        return StaticValue(DatetimeWithFormat(value))

    delta = compile_timedelta(value)
    return RelativeDatetime(delta)


_VALUE_FACTORY_MAP: Dict[str, ValueFunc] = {
    'be_before': _compile_datetime_value,
    'be_after': _compile_datetime_value,
}
_DEFAULT_VALUE_FACTORY: Callable[[object], Value[Any]] = StaticValue


class MatcherFactoryCompiler:

    def __init__(self):
        self._static: Mapping[str, MatcherFactory] = _STATIC_MATCHER_MAP
        self._taking_value: Mapping[str, Tuple[MatcherFunc, ValueFunc]] = {
            key: (matcher_func, _VALUE_FACTORY_MAP.get(key, _DEFAULT_VALUE_FACTORY))
            for (key, matcher_func) in _VALUE_MATCHER_HAMCREST_MAP.items()
        }
        self._taking_matcher: Mapping[str, MatcherFunc] = _RECURSIVE_MATCHERS_HAMCREST_MAP

    def compile(self, obj: object) -> MatcherFactory:
        if isinstance(obj, str) and obj in self._static:
            return self._static[obj]

        if isinstance(obj, Mapping):
            if len(obj) != 1:
                message = f'Must have only 1 element, but has {len(obj)}'
                raise CompilationError(message)

            key, value_obj = next(iter(obj.items()))

            if key in self._taking_value:
                matcher_func, value_func = self._taking_value[key]
                with on_key(key):
                    value = value_func(value_obj)
                return ValueMatcherFactory(matcher_func, value)

            if key in self._taking_matcher:
                matcher_func = self._taking_matcher[key]
                inner_matchers = list(map_compile(self.compile, ensure_list(value_obj)))
                return RecursiveMatcherFactory(matcher_func, inner_matchers)

        return ValueMatcherFactory(hamcrest.equal_to, StaticValue(obj))


def compile_matcher_factory(obj: object) -> MatcherFactory:
    return MatcherFactoryCompiler().compile(obj)
