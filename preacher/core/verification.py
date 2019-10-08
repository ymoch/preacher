"""Verification."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Collection, Iterable, Optional

from .status import Status, StatusedMixin, merge_statuses


@dataclass(frozen=True)
class Verification(StatusedMixin):
    message: Optional[str] = None
    children: Collection[Verification] = tuple()

    @staticmethod
    def skipped() -> Verification:
        return Verification(status=Status.SKIPPED)

    @staticmethod
    def succeed() -> Verification:
        return Verification(status=Status.SUCCESS)

    @staticmethod
    def of_error(error: Exception) -> Verification:
        return Verification(
            status=Status.FAILURE,
            message=f'{error.__class__.__name__}: {error}',
        )


def collect(children: Iterable[Verification]) -> Verification:
    children = list(children)
    status = merge_statuses(child.status for child in children)
    return Verification(status=status, children=children)
