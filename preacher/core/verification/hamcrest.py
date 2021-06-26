"""
Hamcrest custom matchers.
"""
import calendar
import operator
from datetime import datetime
from typing import Callable

from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.description import Description
from hamcrest.core.matcher import Matcher
from hamcrest.library.number.ordering_comparison import OrderingComparison

from preacher.core.datetime import DatetimeWithFormat, ISO8601


class _ConvertingMatcher(BaseMatcher):
    def __init__(self, matcher: BaseMatcher, convert: Callable):
        self._matcher = matcher
        self._convert = convert

    def _matches(self, item) -> bool:
        converted_item = self._convert(item)
        return self._matcher._matches(converted_item)

    def describe_to(self, description: Description) -> None:
        self._matcher.describe_to(description)

    def describe_mismatch(self, item, mismatch_description: Description) -> None:
        converted_item = self._convert(item)
        mismatch_description.append_text("was ").append_description_of(converted_item)


class _DayOfWeekMatcher(BaseMatcher[datetime]):
    def __init__(self, day: int):
        self._day = day

    def _matches(self, item: datetime) -> bool:
        return item.weekday() == self._day

    def describe_to(self, description: Description) -> None:
        name = calendar.day_name[self._day]
        description.append_text(f"is {name}")


def before(value: object) -> Matcher:
    """`value` should be a datetime or DateTimeWithFormat."""
    origin = _ensure_datetime(value)
    matcher = OrderingComparison(origin.value, operator.lt, "before")
    return _ConvertingMatcher(matcher, lambda obj: origin.fmt.parse_datetime(_ensure_str(obj)))


def after(value: object) -> Matcher:
    """`value` should be a datetime or DateTimeWithFormat."""
    origin = _ensure_datetime(value)
    matcher = OrderingComparison(origin.value, operator.gt, "after")
    return _ConvertingMatcher(matcher, lambda obj: origin.fmt.parse_datetime(_ensure_str(obj)))


def day_of_week(day: int) -> Matcher:
    """
    Assert that a datetime value is given on the given "day of week."
    """
    datetime_matcher = _DayOfWeekMatcher(day)
    return _ConvertingMatcher(
        datetime_matcher,
        lambda obj: ISO8601.parse_datetime(_ensure_str(obj)),
    )


def _ensure_str(obj: object) -> str:
    if not isinstance(obj, str):
        raise TypeError(f"Must be a str, but given {type(obj)}: {obj}")
    return obj


def _ensure_datetime(obj: object) -> DatetimeWithFormat:
    if isinstance(obj, DatetimeWithFormat):
        return obj

    if not isinstance(obj, datetime):
        raise TypeError(f"Must be a datetime, but given {type(obj)}: {obj}")
    return DatetimeWithFormat(obj)
