"""Matchers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, List, Optional, TypeVar

from hamcrest import assert_that
from hamcrest.core.matcher import Matcher

from preacher.core.status import Status
from preacher.core.value import Value, ValueContext
from preacher.core.value.impl.static import StaticValue
from .predicate import Predicate
from .verification import Verification

T = TypeVar("T")
MatcherFunc = Callable[..., Matcher]


class MatcherWrappingPredicate(Predicate):
    """Matcher implemented by hamcrest matchers."""

    def __init__(self, factory: MatcherFactory):
        self._factory = factory

    def verify(self, actual: object, context: Optional[ValueContext] = None) -> Verification:
        try:
            hamcrest_matcher = self._factory.create(context)
            assert_that(actual, hamcrest_matcher)
        except AssertionError as error:
            message = str(error).strip()
            return Verification(status=Status.UNSTABLE, message=message)
        except Exception as error:
            return Verification.of_error(error)

        return Verification.succeed()


class MatcherFactory(ABC):
    @abstractmethod
    def create(self, context: Optional[ValueContext] = None) -> Matcher:
        ...  # pragma: no cover


class StaticMatcherFactory(MatcherFactory):
    def __init__(self, matcher: Matcher):
        self._matcher = matcher

    def create(self, context: Optional[ValueContext] = None) -> Matcher:
        return self._matcher


class ValueMatcherFactory(MatcherFactory):
    def __init__(
        self,
        matcher_func: MatcherFunc,
        arg: object,
        value_func: Callable[[object], Value] = StaticValue,
    ):
        self._inner_factory = matcher_func
        self._arg = arg
        self._value_func = value_func

    def create(self, context: Optional[ValueContext] = None) -> Matcher:
        resolved_value = self._ensure_value().resolve(context)
        return self._inner_factory(resolved_value)

    def _ensure_value(self) -> Value:
        if isinstance(self._arg, Value):
            return self._arg
        return self._value_func(self._arg)


class RecursiveMatcherFactory(MatcherFactory):
    def __init__(self, matcher_func: MatcherFunc, inner_factories: List[MatcherFactory]):
        self._matcher_func = matcher_func
        self._inner_factories = inner_factories

    def create(self, context: Optional[ValueContext] = None) -> Matcher:
        inner_matchers = (factory.create(context) for factory in self._inner_factories)
        return self._matcher_func(*inner_matchers)
