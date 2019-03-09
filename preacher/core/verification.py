"""Verification."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Collection, Optional


@dataclass
class Verification:
    is_valid: bool
    message: Optional[str] = None
    children: Collection[Verification] = tuple()
