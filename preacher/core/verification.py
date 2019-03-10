"""Verification."""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
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
    SUCCESS = auto()
    UNSTABLE = auto()
    FAILURE = auto()

    @property
    def is_succeeded(self):
        return self is Status.SUCCESS

    def merge(self, other: Status):
        if self is Status.FAILURE or other is Status.FAILURE:
            return Status.FAILURE
        if self is Status.UNSTABLE or other is Status.UNSTABLE:
            return Status.UNSTABLE
        return Status.SUCCESS


@dataclass
class Verification:
    """
    >>> Verification(Status.SUCCESS).is_valid
    True
    >>> Verification(Status.UNSTABLE).is_valid
    False
    """
    status: Status
    message: Optional[str] = None
    children: Collection[Verification] = tuple()

    @property
    def is_valid(self) -> bool:
        return self.status.is_succeeded
