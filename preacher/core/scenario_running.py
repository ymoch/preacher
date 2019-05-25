"""Scenario running helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .case import CaseResult
from .scenario import Scenario
from .status import Status, merge_statuses


@dataclass
class ScenarioResult:
    label: Optional[str]
    status: Status
    case_results: List[CaseResult]


def run_scenario(scenario: Scenario, base_url: str) -> ScenarioResult:
    """
    When given empty scenario, then runs and returns its result as skipped.
    >>> from unittest.mock import MagicMock, sentinel
    >>> scenario = MagicMock(
    ...     spec=Scenario,
    ...     label=None,
    ...     cases=MagicMock(return_value=iter([]))
    ... )
    >>> result = run_scenario(scenario, base_url='base_url')
    >>> result.label
    >>> result.status
    SKIPPED
    >>> result.case_results
    []

    When given filled scenario, then runs and returns its result.
    >>> sentinel.case_result1.status = Status.UNSTABLE
    >>> case1 = MagicMock(return_value=sentinel.case_result1)
    >>> sentinel.case_result2.status = Status.SUCCESS
    >>> case2 = MagicMock(return_value=sentinel.case_result2)
    >>> scenario = MagicMock(
    ...     spec=Scenario,
    ...     label='label',
    ...     cases=MagicMock(return_value=iter([case1, case2]))
    ... )
    >>> result = run_scenario(scenario, base_url='base_url')
    >>> result.label
    'label'
    >>> result.status
    UNSTABLE
    >>> result.case_results
    [sentinel.case_result1, sentinel.case_result2]
    >>> case1.assert_called_once_with(base_url='base_url')
    >>> case2.assert_called_once_with(base_url='base_url')
    """
    case_results = [case(base_url=base_url) for case in scenario.cases()]
    status = merge_statuses(result.status for result in case_results)
    return ScenarioResult(
        label=scenario.label,
        status=status,
        case_results=case_results,
    )
