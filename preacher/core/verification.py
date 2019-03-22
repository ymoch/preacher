"""Verification."""

from __future__ import annotations
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from functools import reduce, singledispatch
from typing import Collection, Optional


class Status(Enum):
    """
    >>> Status.SUCCESS.is_succeeded
    True
    >>> Status.SUCCESS.merge(Status.SUCCESS).name
    'SUCCESS'
    >>> Status.SUCCESS.merge(Status.UNSTABLE).name
    'UNSTABLE'
    >>> Status.SUCCESS.merge(Status.FAILURE).name
    'FAILURE'

    >>> Status.UNSTABLE.is_succeeded
    False
    >>> Status.UNSTABLE.merge(Status.SUCCESS).name
    'UNSTABLE'
    >>> Status.UNSTABLE.merge(Status.UNSTABLE).name
    'UNSTABLE'
    >>> Status.UNSTABLE.merge(Status.FAILURE).name
    'FAILURE'

    >>> Status.FAILURE.is_succeeded
    False
    >>> Status.FAILURE.merge(Status.SUCCESS).name
    'FAILURE'
    >>> Status.FAILURE.merge(Status.UNSTABLE).name
    'FAILURE'
    >>> Status.FAILURE.merge(Status.FAILURE).name
    'FAILURE'
    """
    # Numbers stand for the priorities for merging.
    SUCCESS = 0
    UNSTABLE = 1
    FAILURE = 2

    @property
    def is_succeeded(self):
        return self is Status.SUCCESS

    def merge(self, other: Status):
        return max(self, other, key=lambda status: status.value)


@singledispatch
def merge_statuses(*args) -> Status:
    """
    >>> merge_statuses(1)
    Traceback (most recent call last):
        ...
    ValueError: (1,)

    For varargs.
    >>> merge_statuses(Status.UNSTABLE).name
    'UNSTABLE'
    >>> merge_statuses(Status.SUCCESS, Status.FAILURE, Status.UNSTABLE).name
    'FAILURE'

    For iterables.
    >>> merge_statuses([]).name
    'SUCCESS'
    >>> merge_statuses([Status.SUCCESS, Status.UNSTABLE, Status.FAILURE]).name
    'FAILURE'
    """
    raise ValueError(str(args))


@merge_statuses.register
def _merge_statuses_for_varargs(*statuses: Status):
    return merge_statuses(statuses)


@merge_statuses.register
def _merge_statuses_for_iterable(statuses: Iterable):
    return reduce(lambda lhs, rhs: lhs.merge(rhs), statuses, Status.SUCCESS)


@dataclass
class Verification:
    status: Status
    message: Optional[str] = None
    children: Collection[Verification] = tuple()

    @staticmethod
    def succeed() -> Verification:
        return Verification(status=Status.SUCCESS)

    @staticmethod
    def of_error(error: Exception) -> Verification:
        return Verification(
            status=Status.FAILURE,
            message=f'{error.__class__.__name__}: {error}',
        )
