"""
Response descriptions, which verify the status code, the headers
and the body.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Mapping, Optional

from preacher.core.extraction import Analyzer, JsonAnalyzer
from preacher.core.request import Response
from preacher.core.status import Status, Statused, merge_statuses
from preacher.core.value import ValueContext
from .description import Description
from .predicate import Predicate
from .response_body import ResponseBodyDescription
from .verification import Verification


@dataclass(frozen=True)
class ResponseVerification(Statused):
    response_id: str
    status: Status = Status.SKIPPED
    status_code: Verification = field(default_factory=Verification)
    headers: Verification = field(default_factory=Verification)
    body: Verification = field(default_factory=Verification)


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
        return Verification.collect(
            predicate.verify(code, context)
            for predicate in self._status_code
        )

    def _verify_headers(
        self,
        headers: Mapping[str, str],
        context: Optional[ValueContext],
    ) -> Verification:
        analyzer = self._analyze_headers(headers)
        return Verification.collect(
            description.verify(analyzer, context)
            for description in self._headers
        )
