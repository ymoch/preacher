"""
Response descriptions, which verify the status code, the headers
and the body.
"""

from dataclasses import dataclass, field
from typing import List, Mapping, Optional

from preacher.core.extraction import MappingAnalyzer, ResponseBodyAnalyzer
from preacher.core.request import Response, ResponseBody
from preacher.core.status import Status, Statused, merge_statuses
from preacher.core.value import ValueContext
from .description import Description
from .predicate import Predicate
from .verification import Verification


@dataclass(frozen=True)
class ResponseVerification(Statused):
    response_id: str
    status_code: Verification = field(default_factory=Verification)
    headers: Verification = field(default_factory=Verification)
    body: Verification = field(default_factory=Verification)

    @property  # HACK should be cached.
    def status(self) -> Status:
        return merge_statuses([self.status_code.status, self.headers.status, self.body.status])


class ResponseDescription:

    def __init__(
        self,
        status_code: Optional[List[Predicate]] = None,
        headers: Optional[List[Description]] = None,
        body: Optional[List[Description]] = None,
    ):
        self._status_code = status_code or []
        self._headers = headers or []
        self._body = body or []

    def verify(
        self,
        response: Response,
        context: Optional[ValueContext] = None,
    ) -> ResponseVerification:
        status_code = self._verify_status_code(response.status_code, context)
        headers = self._verify_headers(response.headers, context)
        body = self._verify_body(response.body, context)

        return ResponseVerification(
            response_id=response.id,
            status_code=status_code,
            headers=headers,
            body=body,
        )

    def _verify_status_code(
        self,
        code: int,
        context: Optional[ValueContext],
    ) -> Verification:
        return Verification.collect(p.verify(code, context) for p in self._status_code)

    def _verify_headers(
        self,
        headers: Mapping[str, str],
        context: Optional[ValueContext],
    ) -> Verification:
        analyzer = MappingAnalyzer(headers)
        return Verification.collect(d.verify(analyzer, context) for d in self._headers)

    def _verify_body(
        self,
        body: ResponseBody,
        context: Optional[ValueContext],
    ) -> Verification:
        analyzer = ResponseBodyAnalyzer(body)
        return Verification.collect(d.verify(analyzer, context) for d in self._body)
