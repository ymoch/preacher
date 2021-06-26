from typing import Iterable

from pytest import mark

from preacher.core.status import Status, merge_statuses


@mark.parametrize(
    ("status", "expected"),
    (
        (Status.SKIPPED, True),
        (Status.SUCCESS, True),
        (Status.UNSTABLE, False),
        (Status.FAILURE, False),
    ),
)
def test_is_succeeded(status: Status, expected: bool):
    assert status.is_succeeded == expected
    assert bool(status) == expected


@mark.parametrize(
    ("lhs", "rhs", "expected"),
    (
        (Status.SKIPPED, Status.SKIPPED, Status.SKIPPED),
        (Status.SKIPPED, Status.SUCCESS, Status.SUCCESS),
        (Status.SKIPPED, Status.UNSTABLE, Status.UNSTABLE),
        (Status.SKIPPED, Status.FAILURE, Status.FAILURE),
        (Status.SUCCESS, Status.SKIPPED, Status.SUCCESS),
        (Status.SUCCESS, Status.SUCCESS, Status.SUCCESS),
        (Status.SUCCESS, Status.UNSTABLE, Status.UNSTABLE),
        (Status.SUCCESS, Status.FAILURE, Status.FAILURE),
        (Status.UNSTABLE, Status.SKIPPED, Status.UNSTABLE),
        (Status.UNSTABLE, Status.SUCCESS, Status.UNSTABLE),
        (Status.UNSTABLE, Status.UNSTABLE, Status.UNSTABLE),
        (Status.UNSTABLE, Status.FAILURE, Status.FAILURE),
        (Status.FAILURE, Status.SKIPPED, Status.FAILURE),
        (Status.FAILURE, Status.SUCCESS, Status.FAILURE),
        (Status.FAILURE, Status.UNSTABLE, Status.FAILURE),
        (Status.FAILURE, Status.FAILURE, Status.FAILURE),
    ),
)
def test_merge(lhs: Status, rhs: Status, expected: Status):
    assert lhs.merge(rhs) is expected


@mark.parametrize(
    ("statuses", "expected"),
    (([], Status.SKIPPED), ([Status.SUCCESS, Status.UNSTABLE, Status.FAILURE], Status.FAILURE)),
)
def test_merge_statuses(statuses: Iterable[Status], expected: Status):
    assert merge_statuses(statuses) is expected
