"""Scenario"""

from __future__ import annotations

from typing import Iterator, List

from .case import Case


class Scenario:
    """
    When given no cases, then skips.
    >>> scenario = Scenario()
    >>> list(scenario.cases())
    []

    When given cases, then run them and returns a result.
    >>> from unittest.mock import sentinel
    >>> scenario = Scenario(cases=[sentinel.case1, sentinel.case2])
    >>> cases = scenario.cases()
    >>> next(cases)
    sentinel.case1
    >>> next(cases)
    sentinel.case2
    """
    def __init__(self: Scenario, cases: List[Case] = []) -> None:
        self._cases = cases

    def cases(self: Scenario) -> Iterator[Case]:
        return iter(self._cases)
