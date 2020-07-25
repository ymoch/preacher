"""Matcher compilation."""

from collections.abc import Mapping
from typing import Callable, Dict, Iterable, Tuple, Union

import hamcrest
from hamcrest.core.matcher import Matcher

from preacher.compilation.error import CompilationError, on_key
from preacher.compilation.util.functional import map_compile
from preacher.compilation.util.type import ensure_list
from preacher.core.value import Value, StaticValue
from preacher.core.verification.matcher import MatcherFactory
from preacher.core.verification.matcher import MatcherFunc
from preacher.core.verification.matcher import RecursiveMatcherFactory
from preacher.core.verification.matcher import StaticMatcherFactory
from preacher.core.verification.matcher import ValueMatcherFactory

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
                message = f'Must have only 1 element, but has {len(obj)}'
                raise CompilationError(message)

            key, value_obj = next(iter(obj.items()))
            if key in self._taking_value:
                return self._compile_taking_value(key, value_obj)
            if key in self._recursive:
                return self._compile_recursive(key, value_obj)

        return ValueMatcherFactory(hamcrest.equal_to, StaticValue(obj))

    def _compile_taking_value(self, key: str, obj: object):
        matcher_func, value_func = self._taking_value[key]
        with on_key(key):
            value = value_func(obj)
        return ValueMatcherFactory(matcher_func, value)

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
