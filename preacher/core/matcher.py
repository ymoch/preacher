from abc import ABC, abstractmethod
from typing import Any, Callable, List, Optional

from hamcrest import assert_that, equal_to
from hamcrest.core.matcher import Matcher as HamcrestMatcher

from .status import Status
from .value import Value
from .verification import Verification


class Matcher(ABC):

    @abstractmethod
    def to_hamcrest(self, **kwargs) -> HamcrestMatcher:
        raise NotImplementedError()

    def verify(self, actual, **kwargs) -> Verification:
        try:
            matcher = self.to_hamcrest(**kwargs)
            assert_that(actual, matcher)
        except AssertionError as error:
            message = str(error).strip()
            return Verification(status=Status.UNSTABLE, message=message)
        except Exception as error:
            return Verification.of_error(error)

        return Verification.succeed()


class StaticMatcher(Matcher):

    def __init__(self, matcher: HamcrestMatcher):
        self._matcher = matcher

    def to_hamcrest(self, **kwargs) -> HamcrestMatcher:
        return self._matcher


class ValueMatcher(Matcher):

    def __init__(self, value: Value):
        self._value = value

    def to_hamcrest(self, **kwargs) -> HamcrestMatcher:
        value_in_context = self._value.apply_context(**kwargs)
        return equal_to(value_in_context)


class SingleValueMatcher(Matcher):

    def __init__(
        self,
        hamcrest_factory: Callable[..., HamcrestMatcher],
        value: Value,
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
            inner_matcher.to_hamcrest()
            for inner_matcher in self._inner_matchers
        )
        return self._hamcrest_factory(*inner_hamcrest_matchers)
