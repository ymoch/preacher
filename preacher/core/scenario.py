"""Scenario"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .case import Case, CaseResult
from .status import Status, merge_statuses


@dataclass
class ScenarioResult:
    status: Status
    case_results: List[CaseResult]


class Scenario:
    """
    When given no cases, then provides a success result.
    >>> scenario = Scenario()
    >>> scenario.cases
    []
    >>> result = scenario(base_url='')
    >>> result.status
    SUCCESS
    >>> result.case_results
    []

    When given cases, then run them and returns a result.
    >>> from unittest.mock import MagicMock
    >>> case1 = MagicMock(return_value=MagicMock(status=Status.UNSTABLE))
    >>> case2 = MagicMock(return_value=MagicMock(status=Status.SUCCESS))
    >>> scenario = Scenario(cases=[case1, case2])
    >>> assert scenario.cases == [case1, case2]
    >>> result = scenario(base_url='url')
    >>> result.status
    UNSTABLE
    >>> result.case_results[0].status
    UNSTABLE
    >>> result.case_results[1].status
    SUCCESS
    >>> case1.assert_called_once_with(base_url='url')
    >>> case2.assert_called_once_with(base_url='url')
    """
    def __init__(self: Scenario, cases: List[Case] = []) -> None:
        self._cases = cases

    def __call__(self: Scenario, base_url: str) -> ScenarioResult:
        case_results = [case(base_url=base_url) for case in self._cases]
        status = merge_statuses(res.status for res in case_results)
        return ScenarioResult(status=status, case_results=case_results)

    @property
    def cases(self: Scenario) -> List[Case]:
        return self._cases
