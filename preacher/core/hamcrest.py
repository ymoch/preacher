from typing import Callable

import hamcrest
from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.matcher import Matcher

from preacher.core.datetime import parse_datetime


class _ConvertingMatcher(BaseMatcher):

    def __init__(self, matcher: BaseMatcher, convert: Callable):
        self._matcher = matcher
        self._convert = convert

    def _matches(self, item):
        datetime_item = self._convert(item)
        return self._matcher._matches(datetime_item)

    def describe_to(self, description):
        self._matcher.describe_to(description)


def _string_datetime_matcher(matcher: BaseMatcher) -> Matcher:
    return _ConvertingMatcher(matcher, parse_datetime)


def before(value) -> Matcher:
    return _string_datetime_matcher(hamcrest.less_than(value))


def after(value) -> Matcher:
    return _string_datetime_matcher(hamcrest.greater_than(value))
