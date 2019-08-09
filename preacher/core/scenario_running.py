"""Scenario running helpers."""

from dataclasses import dataclass
from typing import List, Optional

from .case import CaseResult
from .scenario import Scenario
from .status import Status, merge_statuses


@dataclass(frozen=True)
class ScenarioResult:
    label: Optional[str]
    status: Status
    case_results: List[CaseResult]


def run_scenario(
    scenario: Scenario,
    base_url: str,
    retry: int = 0,
) -> ScenarioResult:
    case_results = [
        case(base_url=base_url, retry=retry)
        for case in scenario.cases()
    ]
    status = merge_statuses(result.status for result in case_results)
    return ScenarioResult(
        label=scenario.label,
        status=status,
        case_results=case_results,
    )
