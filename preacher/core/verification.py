"""Verification."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Collection, Optional

from .status import Status


@dataclass(frozen=True)
class Verification:
    status: Status
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
