from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional

import requests

from preacher.core.datetime import now
from preacher.core.extraction import MappingAnalyzer
from preacher.core.unit import UnitRunner
from preacher.core.value import ValueContext
from preacher.core.verification import Verification
from .case import Case
from .case_listener import CaseListener
from .case_result import CaseResult


@dataclass(frozen=True)
class CaseContext:
    starts: datetime = field(default_factory=now)
    base_url: str = ""


class CaseRunner:
    def __init__(self, unit_runner: UnitRunner, listener: Optional[CaseListener] = None):
        self._unit_runner = unit_runner
        self._listener = listener or CaseListener()

    @property
    def base_url(self) -> str:
        return self._unit_runner.base_url

    def run(
        self,
        case: Case,
        session: Optional[requests.Session] = None,
        context: Optional[Dict[str, object]] = None,
    ) -> CaseResult:
        if not case.enabled:
            return CaseResult(label=case.label)

        starts = now()
        current_context: Dict[str, object] = context or {}
        current_context["base_url"] = self.base_url
        current_context["starts"] = starts

        context_analyzer = MappingAnalyzer(current_context)
        value_context = ValueContext(origin_datetime=starts)
        conditions = Verification.collect(
            condition.verify(context_analyzer, value_context) for condition in case.conditions
        )
        if not conditions.status.is_succeeded:
            return CaseResult(case.label, conditions)

        execution, response, verification = self._unit_runner.run(
            request=case.request,
            requirements=case.response,
            session=session,
        )
        self._listener.on_execution(execution, response)

        return CaseResult(case.label, conditions, execution, verification)
