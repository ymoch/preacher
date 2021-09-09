from typing import Optional

import requests

from preacher.core.context import Context, closed_context
from preacher.core.datetime import now
from preacher.core.extraction import MappingAnalyzer
from preacher.core.unit import UnitRunner
from preacher.core.verification import Verification
from .case import Case
from .case_listener import CaseListener
from .case_result import CaseResult


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
        context: Optional[Context] = None,
    ) -> CaseResult:
        if not case.enabled:
            return CaseResult(label=case.label)

        context = context if context is not None else {}
        with closed_context(context, starts=now(), base_url=self.base_url) as context:
            context_analyzer = MappingAnalyzer(context)
            conditions = Verification.collect(
                condition.verify(context_analyzer, context) for condition in case.conditions
            )
            if not conditions.status.is_succeeded:
                return CaseResult(case.label, conditions)

            execution, response, verification = self._unit_runner.run(
                request=case.request,
                requirements=case.response,
                session=session,
                context=context,
            )
        self._listener.on_execution(execution, response)

        return CaseResult(case.label, conditions, execution, verification)
