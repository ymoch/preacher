"""Verification."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Sequence

from preacher.core.status import Status, Statused, merge_statuses
from preacher.core.util.error import to_message


@dataclass(frozen=True)
class Verification(Statused):
    status: Status = Status.SKIPPED
    message: Optional[str] = None
    children: Sequence[Verification] = ()

    @staticmethod
    def succeed() -> Verification:
        return Verification(status=Status.SUCCESS)

    @staticmethod
    def of_error(error: Exception) -> Verification:
        return Verification(status=Status.FAILURE, message=to_message(error))

    @staticmethod
    def collect(children: Iterable[Verification]) -> Verification:
        children = list(children)
        status = merge_statuses(child.status for child in children)
        return Verification(status=status, children=children)
