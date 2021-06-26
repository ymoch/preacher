"""Scenario"""

from __future__ import annotations

from typing import List, Optional

from preacher.core.verification import Description
from .case import Case


class Scenario:
    def __init__(
        self,
        label: Optional[str] = None,
        ordered: bool = True,
        conditions: Optional[List[Description]] = None,
        cases: Optional[List[Case]] = None,
        subscenarios: Optional[List[Scenario]] = None,
    ):
        self._label = label
        self._ordered = ordered
        self._conditions = conditions or []
        self._cases = cases or []
        self._subscenarios = subscenarios or []

    @property
    def label(self) -> Optional[str]:
        return self._label

    @property
    def ordered(self) -> bool:
        return self._ordered

    @property
    def conditions(self) -> List[Description]:
        return self._conditions

    @property
    def cases(self) -> List[Case]:
        return self._cases

    @property
    def subscenarios(self) -> List[Scenario]:
        return self._subscenarios
