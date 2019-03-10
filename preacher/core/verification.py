"""Verification."""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
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


@dataclass
class Verification:
    status: Status
    message: Optional[str] = None
    children: Collection[Verification] = tuple()
