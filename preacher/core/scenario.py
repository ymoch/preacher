"""Scenario"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator, List, Optional

from .case import Case, CaseResult
from .status import Status, merge_statuses


@dataclass(frozen=True)
class ScenarioResult:
    label: Optional[str]
    status: Status
    message: Optional[str] = None
    case_results: List[CaseResult] = field(default_factory=list)


class Scenario:
    """
    When given no cases, then skips.
    >>> scenario = Scenario()
    >>> scenario.label
    >>> list(scenario.cases())
    []

    When given a label, then returns it.
    >>> scenario = Scenario(label='label')
    >>> scenario.label
    'label'

    When given cases, then iterates them.
    >>> from unittest.mock import sentinel
    >>> scenario = Scenario(cases=[sentinel.case1, sentinel.case2])
    >>> cases = scenario.cases()
    >>> next(cases)
    sentinel.case1
    >>> next(cases)
    sentinel.case2
    """
    def __init__(
        self,
        label: Optional[str] = None,
        cases: List[Case] = [],
    ):
        self._label = label
        self._cases = cases

    @property
    def label(self) -> Optional[str]:
        return self._label

    def cases(self) -> Iterator[Case]:
        return iter(self._cases)

    def run(self, base_url: str, retry: int = 0) -> ScenarioResult:
        case_results = [
            case(base_url=base_url, retry=retry)
            for case in self._cases
        ]
        status = merge_statuses(result.status for result in case_results)
        return ScenarioResult(
            label=self._label,
            status=status,
            case_results=case_results,
        )
