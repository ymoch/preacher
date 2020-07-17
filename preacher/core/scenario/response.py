"""
Response descriptions, which verify the status code, the headers
and the body.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Mapping, Optional

from preacher.core.request import Response
from preacher.core.status import Status, merge_statuses
from preacher.core.value import ValueContext
from .analysis import Analyzer, JsonAnalyzer
from .description import Description
from .predicate import Predicate
from .response_body import ResponseBodyDescription
from .verification import Verification, collect


@dataclass(frozen=True)
class ResponseVerification:
    response_id: str
    status: Status
    status_code: Verification
    headers: Verification
    body: Verification


class ResponseDescription:

    def __init__(
        self,
        status_code: Optional[List[Predicate]] = None,
        headers: Optional[List[Description]] = None,
        body: Optional[ResponseBodyDescription] = None,
        analyze_headers:
            Callable[[Mapping[str, str]], Analyzer] = JsonAnalyzer,
    ):
        self._status_code = status_code or []
        self._headers = headers or []
        self._body = body
        self._analyze_headers = analyze_headers

    def verify(
        self,
        response: Response,
        context: Optional[ValueContext] = None,
    ) -> ResponseVerification:
        status_code = self._verify_status_code(response.status_code, context)

        try:
            headers = self._verify_headers(response.headers, context)
        except Exception as error:
            headers = Verification.of_error(error)

        body = Verification.skipped()
        if self._body:
            body = self._body.verify(response.body, context)

        status = merge_statuses([
            status_code.status,
            headers.status,
            body.status,
        ])
        return ResponseVerification(
            response_id=response.id,
            status=status,
            status_code=status_code,
            headers=headers,
            body=body,
        )

    def _verify_status_code(
        self,
        code: int,
        context: Optional[ValueContext],
    ) -> Verification:
        return collect(
            predicate.verify(code, context)
            for predicate in self._status_code
        )

    def _verify_headers(
        self,
        headers: Mapping[str, str],
        context: Optional[ValueContext],
    ) -> Verification:
        analyzer = self._analyze_headers(headers)
        return collect(
            description.verify(analyzer, context)
            for description in self._headers
        )
