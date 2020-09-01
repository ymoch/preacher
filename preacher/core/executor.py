"""An executor."""

from functools import partial
from typing import Optional, Tuple

import requests

from preacher.core.request import Request, Response, ExecutionReport
from preacher.core.scenario.util.retry import retry_while_false
from preacher.core.value import ValueContext
from preacher.core.verification import ResponseDescription, ResponseVerification

ExecutionResult = Tuple[ExecutionReport, Optional[Response], Optional[ResponseVerification]]


def _predicate(result: ExecutionResult) -> bool:
    execution, _, verification = result
    if not execution.status.is_succeeded:
        return False
    if verification is None:
        return True
    return verification.status.is_succeeded


class Executor:

    def __init__(
        self,
        base_url: str = '',
        retry: int = 0,
        delay: float = 0.1,
        timeout: Optional[float] = None,
        session: Optional[requests.Session] = None,
    ):
        if retry < 0:
            raise ValueError(f'`retry` must be zero or positive, given {retry}')

        self._base_url = base_url
        self._retry = retry
        self._delay = delay
        self._timeout = timeout
        self._session = session

    def execute(self, request: Request, requirements: ResponseDescription) -> ExecutionResult:
        return retry_while_false(
            partial(self._execute, request, requirements),
            attempts=self._retry + 1,
            delay=self._delay,
            predicate=_predicate,
        )

    def _execute(self, request: Request, requirements: ResponseDescription) -> ExecutionResult:
        execution, response = request.execute(
            self._base_url,
            timeout=self._timeout,
            session=self._session,
        )

        if not response:
            return execution, None, None

        context = ValueContext(origin_datetime=execution.starts)
        verification = requirements.verify(response, context)
        return execution, response, verification
