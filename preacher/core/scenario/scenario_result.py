from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from preacher.core.status import Statused, Status, StatusedList
from preacher.core.verification import Verification
from .case_result import CaseResult


@dataclass(frozen=True)
class ScenarioResult(Statused):
    label: Optional[str] = None
    status: Status = Status.SKIPPED
    message: Optional[str] = None
    conditions: Verification = field(default_factory=Verification)
    cases: StatusedList[CaseResult] = field(default_factory=StatusedList)
    subscenarios: StatusedList[ScenarioResult] = field(default_factory=StatusedList)
