"""Verification."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Collection, Optional


@dataclass
class Verification:
    is_valid: bool
    message: Optional[str]
    children: Collection[Verification]
