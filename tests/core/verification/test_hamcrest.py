from datetime import datetime, timezone

from hamcrest.core.string_description import StringDescription
from pytest import mark, raises

from preacher.core.datetime import DatetimeWithFormat
from preacher.core.verification.hamcrest import after, before, day_of_week

ORIGIN = datetime(2019, 12, 15, 12, 34, 56, tzinfo=timezone.utc)


@mark.parametrize(
    "value",
    (
        None,
        1,
        1.2,
        complex(1, 2),
        "str",
    ),
)
def test_datetime_matcher_invalid_creation(value):
    with raises(TypeError):
        before(value)
    with raises(TypeError):
        after(value)


@mark.parametrize("item", [None, 1])
def test_datetime_matcher_invalid_validation(item):
    matcher = before(ORIGIN)
    with raises(TypeError):
        matcher.matches(item)

    matcher = after(ORIGIN)
    with raises(TypeError):
        matcher.matches(item)


@mark.parametrize(
    ("value", "item", "before_expected", "after_expected"),
    (
        (ORIGIN, "2019-12-15T12:34:55Z", True, False),
        (ORIGIN, "2019-12-15T12:34:56Z", False, False),
        (ORIGIN, "2019-12-15T12:34:57Z", False, True),
        (DatetimeWithFormat(ORIGIN), "2019-12-15T12:34:55Z", True, False),
        (DatetimeWithFormat(ORIGIN), "2019-12-15T12:34:56Z", False, False),
        (DatetimeWithFormat(ORIGIN), "2019-12-15T12:34:57Z", False, True),
    ),
)
def test_datetime_matcher(value, item, before_expected, after_expected):
    matcher = before(ORIGIN)
    assert matcher.matches(item) == before_expected
    description = StringDescription()
    matcher.describe_to(description)
    assert str(description).startswith("a value before <")
    description = StringDescription()
    matcher.describe_mismatch(item, description)
    assert str(description).startswith("was <")

    matcher = after(value)
    assert matcher.matches(item) == after_expected
    description = StringDescription()
    matcher.describe_to(description)
    assert str(description).startswith("a value after <")
    description = StringDescription()
    matcher.describe_mismatch(item, description)
    assert str(description).startswith("was <")


@mark.parametrize(
    ("day", "yesterday", "today", "tomorrow", "expected_name"),
    (
        (0, "2021-05-30", "2021-05-31", "2021-06-01", "Monday"),
        (1, "2021-05-31", "2021-06-01", "2021-06-02", "Tuesday"),
        (2, "2021-06-01", "2021-06-02", "2021-06-03", "Wednesday"),
        (3, "2021-06-02", "2021-06-03", "2021-06-04", "Thursday"),
        (4, "2021-06-03", "2021-06-04", "2021-06-05", "Friday"),
        (5, "2021-06-04", "2021-06-05", "2021-06-06", "Saturday"),
        (6, "2021-06-05", "2021-06-06", "2021-06-07", "Sunday"),
    ),
)
def test_day_of_week(day, yesterday, today, tomorrow, expected_name):
    matcher = day_of_week(day)
    assert not matcher.matches(yesterday)
    assert matcher.matches(today)
    assert not matcher.matches(tomorrow)

    description = StringDescription()
    matcher.describe_to(description)
    assert str(description).startswith(f"is {expected_name}")

    description = StringDescription()
    matcher.describe_mismatch(tomorrow, description)
    assert str(description).startswith("was <")


@mark.parametrize(
    ("day", "item", "expected"),
    (
        (0, "2021-05-30", False),
        (0, "2021-05-31", True),
        (0, "2021-06-01", False),
        (1, "2021-05-31", False),
        (1, "2021-06-01", True),
        (1, "2021-06-02", False),
        (2, "2021-06-01", False),
        (2, "2021-06-02", True),
        (2, "2021-06-03", False),
        (3, "2021-06-02", False),
        (3, "2021-06-03", True),
        (3, "2021-06-04", False),
        (4, "2021-06-03", False),
        (4, "2021-06-04", True),
        (4, "2021-06-05", False),
        (5, "2021-06-04", False),
        (5, "2021-06-05", True),
        (5, "2021-06-06", False),
        (6, "2021-05-29", False),
        (6, "2021-05-30", True),
        (6, "2021-05-31", False),
        (6, "2021-05-29T23:59:59.999999", False),
        (6, "2021-05-29T23:59:59.999999Z", False),
        (6, "2021-05-29T23:59:59.999999+09:00", False),
        (6, "2021-05-30T00:00:00.000000", True),
        (6, "2021-05-30T00:00:00.000000Z", True),
        (6, "2021-05-30T00:00:00.000000+09:00", True),
        (6, "2021-05-30T23:59:59.000000", True),
        (6, "2021-05-30T23:59:59.000000Z", True),
        (6, "2021-05-30T23:59:59.000000+09:00", True),
        (6, "2021-05-31T00:00:00.000000", False),
        (6, "2021-05-31T00:00:00.000000Z", False),
        (6, "2021-05-31T00:00:00.000000+09:00", False),
    ),
)
def test_day_of_week_matching(day: int, item: datetime, expected: bool):
    assert day_of_week(day).matches(item) == expected


@mark.parametrize(
    ("day", "expected_description"),
    (
        (0, "is Monday"),
        (1, "is Tuesday"),
        (2, "is Wednesday"),
        (3, "is Thursday"),
        (4, "is Friday"),
        (5, "is Saturday"),
        (6, "is Sunday"),
    ),
)
def test_day_of_week_description(day: int, expected_description: str):
    matcher = day_of_week(day)

    description = StringDescription()
    matcher.describe_to(description)
    assert str(description).startswith(expected_description)

    description = StringDescription()
    matcher.describe_mismatch("2021-05-29", description)
    assert str(description).startswith("was <")
