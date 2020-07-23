"""Matchers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Generic, List, Optional, TypeVar

from hamcrest import assert_that
from hamcrest.core.matcher import Matcher as HamcrestMatcher

from preacher.core.status import Status
from preacher.core.value import Value, ValueContext
from .verification import Verification

T = TypeVar('T')


class Matcher(ABC):
    """Matcher interfaces."""

    @abstractmethod
    def match(self, actual: object, context: Optional[ValueContext] = None) -> Verification:
        raise NotImplementedError()


class HamcrestWrappingMatcher(Matcher):
    """Matcher implemented by hamcrest matchers."""

    def __init__(self, factory: HamcrestFactory):
        self._factory = factory

    def match(self, actual: object, context: Optional[ValueContext] = None) -> Verification:
        return match(self._factory, actual, context)


class HamcrestFactory(ABC):

    @abstractmethod
    def create(self, context: Optional[ValueContext] = None) -> HamcrestMatcher:
        raise NotImplementedError()


class StaticHamcrestFactory(HamcrestFactory):

    def __init__(self, hamcrest: HamcrestMatcher):
        self._hamcrest = hamcrest

    def create(self, context: Optional[ValueContext] = None) -> HamcrestMatcher:
        return self._hamcrest


class ValueHamcrestFactory(HamcrestFactory, Generic[T]):

    def __init__(self, hamcrest_factory: Callable[..., HamcrestMatcher], value: Value[T]):
        self._hamcrest_factory = hamcrest_factory
        self._value = value

    def create(self, context: Optional[ValueContext] = None) -> HamcrestMatcher:
        resolved_value = self._value.resolve(context)
        return self._hamcrest_factory(resolved_value)


class RecursiveHamcrestFactory(HamcrestFactory):

    def __init__(
        self,
        hamcrest_factory: Callable[..., HamcrestMatcher],
        inner_matchers: List[HamcrestFactory],
    ):
        self._hamcrest_factory = hamcrest_factory
        self._inner_matchers = inner_matchers

    def create(self, context: Optional[ValueContext] = None) -> HamcrestMatcher:
        inner_hamcrest_matchers = (
            inner_matcher.create(context)
            for inner_matcher in self._inner_matchers
        )
        return self._hamcrest_factory(*inner_hamcrest_matchers)


def match(
    matcher: HamcrestFactory,
    actual: object,
    context: Optional[ValueContext] = None,
) -> Verification:
    try:
        hamcrest_matcher = matcher.create(context)
        assert_that(actual, hamcrest_matcher)
    except AssertionError as error:
        message = str(error).strip()
        return Verification(status=Status.UNSTABLE, message=message)
    except Exception as error:
        return Verification.of_error(error)

    return Verification.succeed()
