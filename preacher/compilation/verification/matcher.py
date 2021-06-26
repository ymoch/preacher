"""Matcher compilation."""

from collections.abc import Mapping
from typing import Callable, Dict, Iterable, Tuple, Union

import hamcrest
from hamcrest.core.matcher import Matcher

from preacher.compilation.error import CompilationError, on_key
from preacher.compilation.util.functional import map_compile
from preacher.compilation.util.type import ensure_list
from preacher.core.value import Value
from preacher.core.value.impl.datetime import parse_datetime_value_with_format
from preacher.core.value.impl.static import StaticValue
from preacher.core.verification.hamcrest import before, after, day_of_week
from preacher.core.verification.matcher import MatcherFactory
from preacher.core.verification.matcher import MatcherFunc
from preacher.core.verification.matcher import RecursiveMatcherFactory
from preacher.core.verification.matcher import StaticMatcherFactory
from preacher.core.verification.matcher import ValueMatcherFactory
from preacher.core.verification.type import require_type

ValueFunc = Callable[[object], Value]


class MatcherFactoryCompiler:
    """
    A matcher factory compiler.
    """

    _DEFAULT_VALUE_FUNC = StaticValue

    def __init__(self):
        self._static: Dict[str, MatcherFactory] = {}
        self._taking_value: Dict[str, Tuple[MatcherFunc, ValueFunc]] = {}
        self._recursive: Dict[str, Tuple[MatcherFunc, bool]] = {}

    def add_static(
        self,
        keys: Union[str, Iterable[str]],
        item: Union[MatcherFactory, Matcher],
    ) -> None:
        """
        Add a static matcher on given keys.

        Args:
            keys: The key(s) of the matcher.
            item: A matcher or a ``MatcherFactory`` to assign.
        """

        if isinstance(item, Matcher):
            item = StaticMatcherFactory(item)
        for key in self._ensure_keys(keys):
            self._static[key] = item

    def add_taking_value(
        self,
        keys: Union[str, Iterable[str]],
        matcher_func: MatcherFunc,
        value_func: ValueFunc = _DEFAULT_VALUE_FUNC,
    ) -> None:
        """
        Add a matcher taking a value on given keys.

        Args:
            keys: The key(s) of the matcher.
            matcher_func: A function that takes an object and returns a matcher.
            value_func (optional): A function that takes an object and returns a ``Value`` object.
        """

        for key in self._ensure_keys(keys):
            self._taking_value[key] = (matcher_func, value_func)

    def add_recursive(
        self,
        keys: Union[str, Iterable[str]],
        matcher_func: MatcherFunc,
        multiple: bool = True,
    ) -> None:
        """
        Add a matcher taking one or more matchers.

        Args:
            keys: The key(s) of the matcher.
            matcher_func: A function that takes one or more matchers and returns a matcher.
            multiple: Whether the matcher can take multiple arguments or not.
        """

        for key in self._ensure_keys(keys):
            self._recursive[key] = (matcher_func, multiple)

    def compile(self, obj: object) -> MatcherFactory:
        """
        Compile an object into a matcher factory.

        Args:
            obj: A compiled object.
        Returns:
            The result of compilation.
        Raises:
            CompilationError: when compilation fails.
        """

        if isinstance(obj, str) and obj in self._static:
            return self._static[obj]

        if isinstance(obj, Mapping):
            if len(obj) != 1:
                message = f"Must have only 1 element, but has {len(obj)}"
                raise CompilationError(message)

            key, value_obj = next(iter(obj.items()))
            if key in self._taking_value:
                return self._compile_taking_value(key, value_obj)
            if key in self._recursive:
                return self._compile_recursive(key, value_obj)

        return ValueMatcherFactory(hamcrest.equal_to, StaticValue(obj))

    def _compile_taking_value(self, key: str, obj: object):
        matcher_func, value_func = self._taking_value[key]
        return ValueMatcherFactory(matcher_func, arg=obj, value_func=value_func)

    def _compile_recursive(self, key: str, obj: object):
        matcher_func, multiple = self._recursive[key]
        if multiple:
            objs = ensure_list(obj)
            inner_matchers = list(map_compile(self.compile, objs))
        else:
            with on_key(key):
                inner_matchers = [self.compile(obj)]
        return RecursiveMatcherFactory(matcher_func, inner_matchers)

    @staticmethod
    def _ensure_keys(keys: Union[str, Iterable[str]]) -> Iterable[str]:
        if isinstance(keys, str):
            return (keys,)
        return keys


def add_default_matchers(compiler: MatcherFactoryCompiler) -> None:
    """
    Add default matchers to a compiler.

    Args:
        compiler: A compiler to be modified.
    """

    compiler.add_recursive(("be",), hamcrest.is_, multiple=False)

    # For objects.
    compiler.add_static(("be_null",), hamcrest.none())
    compiler.add_static(("not_be_null",), hamcrest.not_none())
    compiler.add_static(("be_monday",), day_of_week(0))
    compiler.add_static(("be_tuesday",), day_of_week(1))
    compiler.add_static(("be_wednesday",), day_of_week(2))
    compiler.add_static(("be_thursday",), day_of_week(3))
    compiler.add_static(("be_friday",), day_of_week(4))
    compiler.add_static(("be_saturday",), day_of_week(5))
    compiler.add_static(("be_sunday",), day_of_week(6))
    compiler.add_taking_value(("equal",), hamcrest.equal_to)
    compiler.add_recursive(("have_length",), hamcrest.has_length, multiple=False)

    # For comparable values.
    compiler.add_taking_value(("be_greater_than",), hamcrest.greater_than)
    compiler.add_taking_value(("be_greater_than_or_equal_to",), hamcrest.greater_than_or_equal_to)
    compiler.add_taking_value(("be_less_than",), hamcrest.less_than)
    compiler.add_taking_value(("be_less_than_or_equal_to",), hamcrest.less_than_or_equal_to)

    # For strings.
    compiler.add_taking_value(("contain_string",), require_type(str, hamcrest.contains_string))
    compiler.add_taking_value(("start_with",), require_type(str, hamcrest.starts_with))
    compiler.add_taking_value(("end_with",), require_type(str, hamcrest.ends_with))
    compiler.add_taking_value(("match_regexp",), require_type(str, hamcrest.matches_regexp))

    # For collections.
    compiler.add_recursive(("have_item",), hamcrest.has_item, multiple=False)
    compiler.add_recursive(("have_items",), hamcrest.has_items)
    compiler.add_recursive(("contain_exactly",), hamcrest.contains_exactly)
    compiler.add_recursive(("contain_in_any_order",), hamcrest.contains_inanyorder)

    # For datetime.
    compiler.add_taking_value(("be_before",), before, parse_datetime_value_with_format)
    compiler.add_taking_value(("be_after",), after, parse_datetime_value_with_format)

    # For collections.
    compiler.add_static(("be_empty",), StaticMatcherFactory(hamcrest.empty()))

    # Logical.
    compiler.add_static("anything", StaticMatcherFactory(hamcrest.anything()))
    compiler.add_recursive(("not",), hamcrest.not_, multiple=False)
    compiler.add_recursive(("all_of",), hamcrest.all_of)
    compiler.add_recursive(("any_of",), hamcrest.any_of)
