"""
Response descriptions, which verify the status code, the headers
and the body.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from preacher.core.extraction import ResponseBodyAnalyzer, MappingAnalyzer
from preacher.core.request import Response
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
        status_code = Verification.collect(
            p.verify(response.status_code, context) for p in self._status_code
        )

        header_analyzer = MappingAnalyzer(response.headers)
        headers = Verification.collect(d.verify(header_analyzer, context) for d in self._headers)

        body_analyzer = ResponseBodyAnalyzer(response.body)
        body = Verification.collect(d.verify(body_analyzer, context) for d in self._body)

        return ResponseVerification(
            response_id=response.id,
            status_code=status_code,
            headers=headers,
            body=body,
        )
