"""
Response descriptions, which verify the status code, the headers
and the body.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Mapping, Optional

from preacher.core.response import Response
from .analysis import Analyzer, JsonAnalyzer
from .body_description import BodyDescription
from .analysis_description import AnalysisDescription
from .predicate import Predicate
from .status import Status, merge_statuses
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
        headers: Optional[List[AnalysisDescription]] = None,
        body: Optional[BodyDescription] = None,
        analyze_headers:
            Callable[[Mapping[str, str]], Analyzer] = JsonAnalyzer,
    ):
        self._status_code = status_code or []
        self._headers = headers or []
        self._body = body
        self._analyze_headers = analyze_headers

    def verify(self, response: Response, **kwargs) -> ResponseVerification:
        """`**kwargs` will be delegated to descriptions."""
        status_code = self._verify_status_code(response.status_code, **kwargs)

        try:
            headers = self._verify_headers(response.headers, **kwargs)
        except Exception as error:
            headers = Verification.of_error(error)

        body = Verification.skipped()
        if self._body:
            body = self._body.verify(response.body, **kwargs)

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

    def _verify_status_code(self, code: int, **kwargs) -> Verification:
        return collect(
            predicate.verify(code, **kwargs)
            for predicate in self._status_code
        )

    def _verify_headers(
        self,
        headers: Mapping[str, str],
        **kwargs
    ) -> Verification:
        analyzer = self._analyze_headers(headers)
        return collect(
            description.verify(analyzer, **kwargs)
            for description in self._headers
        )
