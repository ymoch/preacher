"""Status."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass, field
from enum import Enum
from functools import reduce
from typing import Generic, List, TypeVar


class Status(Enum):

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
    return reduce(lambda lhs, rhs: lhs.merge(rhs), statuses, Status.SKIPPED)


class Statused(ABC):
    @property
    @abstractmethod
    def status(self) -> Status:
        ...  # pragma: no cover


StatusedType = TypeVar("StatusedType", bound=Statused)


@dataclass(frozen=True)
class StatusedList(Generic[StatusedType], Statused):
    items: List[StatusedType] = field(default_factory=list)

    @property
    def status(self) -> Status:  # HACK: should be cached
        return merge_statuses(item.status for item in self.items)

    @staticmethod
    def collect(
        iterable: Iterable[StatusedType],
    ) -> StatusedList[StatusedType]:
        return StatusedList(list(iterable))
