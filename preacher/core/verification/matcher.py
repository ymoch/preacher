"""Matchers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Generic, List, Optional, TypeVar

from hamcrest import assert_that
from hamcrest.core.matcher import Matcher

from preacher.core.status import Status
from preacher.core.value import Value, ValueContext
from .predicate import Predicate
from .verification import Verification

T = TypeVar('T')


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
        raise NotImplementedError()


class StaticMatcherFactory(MatcherFactory):

    def __init__(self, hamcrest: Matcher):
        self._hamcrest = hamcrest

    def create(self, context: Optional[ValueContext] = None) -> Matcher:
        return self._hamcrest


class ValueMatcherFactory(MatcherFactory, Generic[T]):

    def __init__(self, hamcrest_factory: Callable[..., Matcher], value: Value[T]):
        self._hamcrest_factory = hamcrest_factory
        self._value = value

    def create(self, context: Optional[ValueContext] = None) -> Matcher:
        resolved_value = self._value.resolve(context)
        return self._hamcrest_factory(resolved_value)


class RecursiveMatcherFactory(MatcherFactory):

    def __init__(
        self,
        hamcrest_factory: Callable[..., Matcher],
        inner_matchers: List[MatcherFactory],
    ):
        self._hamcrest_factory = hamcrest_factory
        self._inner_matchers = inner_matchers

    def create(self, context: Optional[ValueContext] = None) -> Matcher:
        inner_hamcrest_matchers = (
            inner_matcher.create(context)
            for inner_matcher in self._inner_matchers
        )
        return self._hamcrest_factory(*inner_hamcrest_matchers)
