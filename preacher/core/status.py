"""Status."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from functools import reduce, singledispatch
from typing import (
    Iterable as IterableType,
    Iterator,
    Sequence,
    TypeVar,
    Union,
)


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
    SKIPPED
    >>> merge_statuses([Status.SUCCESS, Status.UNSTABLE, Status.FAILURE])
    FAILURE
    """
    raise ValueError(str(args))


@merge_statuses.register
def _merge_statuses_for_varargs(*statuses: Status):
    return merge_statuses(statuses)


@merge_statuses.register
def _merge_statuses_for_iterable(statuses: Iterable):
    return reduce(lambda lhs, rhs: lhs.merge(rhs), statuses, Status.SKIPPED)


@dataclass(frozen=True)
class StatusedMixin:
    status: Status = Status.SKIPPED


class StatusedInterface(ABC):
    """
    >>> class ConcreteStatused(StatusedInterface):
    ...     @property
    ...     def status(self) -> Status:
    ...         return super().status
    >>> ConcreteStatused().status
    SKIPPED
    """
    @property
    @abstractmethod
    def status(self) -> Status:
        return Status.SKIPPED


class StatusedSequence(StatusedInterface, Sequence[T]):
    """
    >>> bool(StatusedSequence())
    False
    >>> bool(StatusedSequence(Status.SUCCESS, []))
    False
    >>> bool(StatusedSequence(Status.FAILURE, [1]))
    True
    """

    def __init__(
        self,
        status: Status = Status.SKIPPED,
        items: Sequence[T] = [],
    ):
        self._status = status
        self._items = items

    @property
    def status(self) -> Status:
        return self._status

    def __bool__(self) -> bool:
        return bool(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[T]:
        return iter(self._items)

    def __getitem__(self, key):
        return self._items[key]


Statused = Union[StatusedMixin, StatusedInterface]
StatusedType = TypeVar('StatusedType', bound=Statused)


def collect_statused(
    items: IterableType[StatusedType],
) -> StatusedSequence[StatusedType]:
    items = list(items)
    status = merge_statuses(item.status for item in items)
    return StatusedSequence(status=status, items=items)
