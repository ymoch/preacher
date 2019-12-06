from typing import Any, Callable

from hamcrest import assert_that
from hamcrest.core.matcher import Matcher as HamcrestMatcher

from .status import Status
from .value import Value
from .verification import Verification


class Matcher:

    def __init__(
        self,
        hamcrest_matcher_factory: Callable[[Any], HamcrestMatcher],
        value: Value[Any],
    ):
        self._factory = hamcrest_matcher_factory
        self._value = value

    def verify(self, actual: Any) -> Verification:
        try:
            value_in_context = self._value.apply_context()
            hamcrest_matcher = self._factory(value_in_context)
            assert_that(actual, hamcrest_matcher)
        except AssertionError as error:
            message = str(error).strip()
            return Verification(status=Status.UNSTABLE, message=message)
        except Exception as error:
            return Verification.of_error(error)

        return Verification.succeed()
