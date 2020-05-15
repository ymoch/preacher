"""
Hamcrest custom matchers.
"""

import operator
from datetime import datetime
from typing import Callable, Optional

from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.matcher import Matcher
from hamcrest.library.number.ordering_comparison import OrderingComparison

from preacher.core.datetime import parse_datetime


class _ConvertingMatcher(BaseMatcher):

    def __init__(self, matcher: BaseMatcher, convert: Callable):
        self._matcher = matcher
        self._convert = convert

    def _matches(self, item):
        converted_item = self._convert(item)
        return self._matcher._matches(converted_item)

    def describe_to(self, description):
        self._matcher.describe_to(description)

    def describe_mismatch(self, item, mismatch_description):
        converted_item = self._convert(item)
        mismatch_description.append_text('was ').append_description_of(
            converted_item
        )


def _convert_to_datetime(value: object) -> Optional[datetime]:
    if not isinstance(value, str):
        raise TypeError(f'Must be a string, but given {value}')
    return parse_datetime(value)


def _string_datetime_matcher(matcher: BaseMatcher) -> Matcher:
    return _ConvertingMatcher(matcher, _convert_to_datetime)


def before(value: object) -> Matcher:
    return _string_datetime_matcher(
        OrderingComparison(value, operator.lt, "before")
    )


def after(value: object) -> Matcher:
    return _string_datetime_matcher(
        OrderingComparison(value, operator.gt, "after")
    )
