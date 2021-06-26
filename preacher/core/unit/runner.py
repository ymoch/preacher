"""An executor."""

from functools import partial
from typing import Optional, Tuple

import requests

from preacher.core.request import Request, Response, Requester, ExecutionReport
from preacher.core.scenario.util.retry import retry_while_false
from preacher.core.value import ValueContext
from preacher.core.verification import ResponseDescription, ResponseVerification

Result = Tuple[ExecutionReport, Optional[Response], Optional[ResponseVerification]]


def predicate(result: Result) -> bool:
    execution, _, verification = result
    if not execution.status.is_succeeded:
        return False
    if verification is None:
        return True
    return verification.status.is_succeeded


class UnitRunner:
    def __init__(self, requester: Requester, retry: int = 0, delay: float = 0.1):
        if retry < 0:
            raise ValueError(f"`retry` must be zero or positive, given {retry}")

        self._requester = requester
        self._retry = retry
        self._delay = delay

    @property
    def base_url(self) -> str:
        return self._requester.base_url

    def run(
        self,
        request: Request,
        requirements: ResponseDescription,
        session: Optional[requests.Session] = None,
    ) -> Result:
        return retry_while_false(
            partial(self._execute, request, requirements, session),
            attempts=self._retry + 1,
            delay=self._delay,
            predicate=predicate,
        )

    def _execute(
        self,
        request: Request,
        requirements: ResponseDescription,
        session: Optional[requests.Session] = None,
    ) -> Result:
        execution, response = self._requester.execute(request, session=session)
        if not response:
            return execution, None, None

        context = ValueContext(origin_datetime=execution.starts)
        verification = requirements.verify(response, context)
        return execution, response, verification
