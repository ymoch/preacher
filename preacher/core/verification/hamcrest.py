"""
Hamcrest custom matchers.
"""

import operator
from datetime import datetime
from typing import Callable

from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.matcher import Matcher
from hamcrest.library.number.ordering_comparison import OrderingComparison

from preacher.core.datetime import DatetimeWithFormat


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
        mismatch_description.append_text('was ').append_description_of(converted_item)


def before(value: object) -> Matcher:
    """`value` should be a datetime or DateTimeWithFormat."""
    origin = _ensure_datetime(value)
    matcher = OrderingComparison(origin.value, operator.lt, 'before')
    return _ConvertingMatcher(matcher, lambda obj: origin.fmt.parse_datetime(_ensure_str(obj)))


def after(value: object) -> Matcher:
    """`value` should be a datetime or DateTimeWithFormat."""
    origin = _ensure_datetime(value)
    matcher = OrderingComparison(origin.value, operator.gt, 'after')
    return _ConvertingMatcher(matcher, lambda obj: origin.fmt.parse_datetime(_ensure_str(obj)))


def _ensure_str(obj: object) -> str:
    if not isinstance(obj, str):
        raise TypeError(f'Must be a str, but given {type(obj)}: {obj}')
    return obj


def _ensure_datetime(obj: object) -> DatetimeWithFormat:
    if isinstance(obj, DatetimeWithFormat):
        return obj

    if not isinstance(obj, datetime):
        raise TypeError(f'Must be a datetime, but given {type(obj)}: {obj}')
    return DatetimeWithFormat(obj)
