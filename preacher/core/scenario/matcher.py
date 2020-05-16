"""Matchers."""

from abc import ABC, abstractmethod
from typing import Callable, Generic, List, TypeVar

from hamcrest import assert_that
from hamcrest.core.matcher import Matcher as HamcrestMatcher

from preacher.core.interpretation.value import Value
from .status import Status
from .verification import Verification

T = TypeVar('T')


class Matcher(ABC):
    """
    Matcher interfaces.
    Matchers are implemented as factories of Hamcrest matchers.
    """

    @abstractmethod
    def to_hamcrest(self, **kwargs) -> HamcrestMatcher:
        raise NotImplementedError()


class StaticMatcher(Matcher):

    def __init__(self, hamcrest: HamcrestMatcher):
        self._hamcrest = hamcrest

    def to_hamcrest(self, **kwargs) -> HamcrestMatcher:
        return self._hamcrest


class ValueMatcher(Matcher, Generic[T]):

    def __init__(
        self,
        hamcrest_factory: Callable[..., HamcrestMatcher],
        value: Value[T],
    ):
        self._hamcrest_factory = hamcrest_factory
        self._value = value

    def to_hamcrest(self, **kwargs) -> HamcrestMatcher:
        value_in_context = self._value.apply_context(**kwargs)
        return self._hamcrest_factory(value_in_context)


class RecursiveMatcher(Matcher):

    def __init__(
        self,
        hamcrest_factory: Callable[..., HamcrestMatcher],
        inner_matchers: List[Matcher],
    ):
        self._hamcrest_factory = hamcrest_factory
        self._inner_matchers = inner_matchers

    def to_hamcrest(self, **kwargs) -> HamcrestMatcher:
        inner_hamcrest_matchers = (
            inner_matcher.to_hamcrest(**kwargs)
            for inner_matcher in self._inner_matchers
        )
        return self._hamcrest_factory(*inner_hamcrest_matchers)


def match(matcher: Matcher, actual: object, **kwargs) -> Verification:
    try:
        hamcrest_matcher = matcher.to_hamcrest(**kwargs)
        assert_that(actual, hamcrest_matcher)
    except AssertionError as error:
        message = str(error).strip()
        return Verification(status=Status.UNSTABLE, message=message)
    except Exception as error:
        return Verification.of_error(error)

    return Verification.succeed()
