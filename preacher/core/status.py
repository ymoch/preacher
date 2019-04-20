"""Status."""

from __future__ import annotations

from collections.abc import Iterable
from enum import Enum
from functools import reduce, singledispatch


class Status(Enum):
    """
    >>> Status.SUCCESS.is_succeeded
    True
    >>> Status.SUCCESS.merge(Status.SUCCESS)
    SUCCESS
    >>> Status.SUCCESS.merge(Status.UNSTABLE)
    UNSTABLE
    >>> Status.SUCCESS.merge(Status.FAILURE)
    FAILURE

    >>> Status.UNSTABLE.is_succeeded
    False
    >>> Status.UNSTABLE.merge(Status.SUCCESS)
    UNSTABLE
    >>> Status.UNSTABLE.merge(Status.UNSTABLE)
    UNSTABLE
    >>> Status.UNSTABLE.merge(Status.FAILURE)
    FAILURE

    >>> Status.FAILURE.is_succeeded
    False
    >>> Status.FAILURE.merge(Status.SUCCESS)
    FAILURE
    >>> Status.FAILURE.merge(Status.UNSTABLE)
    FAILURE
    >>> Status.FAILURE.merge(Status.FAILURE)
    FAILURE
    """
    # Numbers stand for the priorities for merging.
    SUCCESS = 0
    UNSTABLE = 1
    FAILURE = 2

    @property
    def is_succeeded(self: Status):
        return self is Status.SUCCESS

    def merge(self: Status, other: Status):
        return max(self, other, key=lambda status: status.value)

    def __str__(self: Status) -> str:
        return self.name

    def __repr__(self: Status) -> str:
        return str(self)


@singledispatch
def merge_statuses(*args) -> Status:
    """
    >>> merge_statuses(1)
    Traceback (most recent call last):
        ...
    ValueError: (1,)

    For varargs.
    >>> merge_statuses(Status.UNSTABLE)
    UNSTABLE
    >>> merge_statuses(Status.SUCCESS, Status.FAILURE, Status.UNSTABLE)
    FAILURE

    For iterables.
    >>> merge_statuses([])
    SUCCESS
    >>> merge_statuses([Status.SUCCESS, Status.UNSTABLE, Status.FAILURE])
    FAILURE
    """
    raise ValueError(str(args))


@merge_statuses.register
def _merge_statuses_for_varargs(*statuses: Status):
    return merge_statuses(statuses)


@merge_statuses.register
def _merge_statuses_for_iterable(statuses: Iterable):
    return reduce(lambda lhs, rhs: lhs.merge(rhs), statuses, Status.SUCCESS)
