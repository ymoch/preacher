"""Scenario"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .case import Case, CaseResult
from .status import Status, merge_statuses


@dataclass(frozen=True)
class ScenarioResult:
    label: Optional[str]
    status: Status
    message: Optional[str] = None
    case_results: List[CaseResult] = field(default_factory=list)


class Scenario:

    def __init__(
        self,
        label: Optional[str] = None,
        cases: List[Case] = [],
    ):
        self._label = label
        self._cases = cases

    def run(
        self,
        base_url: str,
        retry: int = 0,
        delay: float = 0.1,
        timeout: Optional[float] = None,
    ) -> ScenarioResult:
        case_results = [
            case(base_url, timeout=timeout, retry=retry, delay=delay)
            for case in self._cases
        ]
        status = merge_statuses(result.status for result in case_results)
        return ScenarioResult(
            label=self._label,
            status=status,
            case_results=case_results,
        )
