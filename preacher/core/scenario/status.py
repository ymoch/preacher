"""Status."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from enum import Enum
from functools import reduce
from typing import Generic, List, TypeVar

T = TypeVar('T')


class Status(Enum):
    """
    >>> Status.SKIPPED.is_succeeded
    True
    >>> bool(Status.SKIPPED)
    True
    >>> Status.SKIPPED.merge(Status.SUCCESS)
    SUCCESS
    >>> Status.SKIPPED.merge(Status.UNSTABLE)
    UNSTABLE
    >>> Status.SKIPPED.merge(Status.FAILURE)
    FAILURE

    >>> Status.SUCCESS.is_succeeded
    True
    >>> bool(Status.SUCCESS)
    True
    >>> Status.SUCCESS.merge(Status.SKIPPED)
    SUCCESS
    >>> Status.SUCCESS.merge(Status.SUCCESS)
    SUCCESS
    >>> Status.SUCCESS.merge(Status.UNSTABLE)
    UNSTABLE
    >>> Status.SUCCESS.merge(Status.FAILURE)
    FAILURE

    >>> Status.UNSTABLE.is_succeeded
    False
    >>> bool(Status.UNSTABLE)
    False
    >>> Status.UNSTABLE.merge(Status.SKIPPED)
    UNSTABLE
    >>> Status.UNSTABLE.merge(Status.SUCCESS)
    UNSTABLE
    >>> Status.UNSTABLE.merge(Status.UNSTABLE)
    UNSTABLE
    >>> Status.UNSTABLE.merge(Status.FAILURE)
    FAILURE

    >>> Status.FAILURE.is_succeeded
    False
    >>> bool(Status.FAILURE)
    False
    >>> Status.FAILURE.merge(Status.SKIPPED)
    FAILURE
    >>> Status.FAILURE.merge(Status.SUCCESS)
    FAILURE
    >>> Status.FAILURE.merge(Status.UNSTABLE)
    FAILURE
    >>> Status.FAILURE.merge(Status.FAILURE)
    FAILURE
    """
    # Numbers stand for the priorities for merging.
    SKIPPED = 0
    SUCCESS = 1
    UNSTABLE = 2
    FAILURE = 3

    @property
    def is_succeeded(self):
        return self.value <= Status.SUCCESS.value

    def merge(self, other: Status):
        return max(self, other, key=lambda status: status.value)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return str(self)

    def __bool__(self) -> bool:
        return self.is_succeeded


def merge_statuses(statuses: Iterable[Status]) -> Status:
    """
    >>> merge_statuses([])
    SKIPPED
    >>> merge_statuses([Status.SUCCESS, Status.UNSTABLE, Status.FAILURE])
    FAILURE
    """
    return reduce(lambda lhs, rhs: lhs.merge(rhs), statuses, Status.SKIPPED)


@dataclass(frozen=True)
class StatusedMixin:
    status: Status = Status.SKIPPED


@dataclass(frozen=True)
class StatusedList(Generic[T], StatusedMixin):
    items: List[T] = field(default_factory=list)


Statused = TypeVar('Statused', bound=StatusedMixin)


def collect_statused(
    items: Iterable[Statused],
) -> StatusedList[Statused]:
    items = list(items)
    status = merge_statuses(item.status for item in items)
    return StatusedList(status=status, items=items)
