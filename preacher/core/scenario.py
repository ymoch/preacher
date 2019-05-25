"""Scenario"""

from __future__ import annotations

from typing import Iterator, List, Optional

from .case import Case


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
        self: Scenario,
        label: Optional[str] = None,
        cases: List[Case] = [],
    ) -> None:
        self._label = label
        self._cases = cases

    @property
    def label(self: Scenario) -> Optional[str]:
        return self._label

    def cases(self: Scenario) -> Iterator[Case]:
        return iter(self._cases)
