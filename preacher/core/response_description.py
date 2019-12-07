"""Response descriptions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, List, Mapping, Optional

from preacher.core.request import Response
from .analysis import Analyzer, JsonAnalyzer
from .body_description import BodyDescription
from .description import Description
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
        status_code_predicates: Optional[List[Predicate]] = None,
        headers_descriptions: Optional[List[Description]] = None,
        body_description: Optional[BodyDescription] = None,
        analyze_headers:
            Callable[[Mapping[str, str]], Analyzer] = JsonAnalyzer,
    ):
        self._status_code_predicates = status_code_predicates or []
        self._headers_descriptions = headers_descriptions or []
        self._body_description = body_description
        self._analyze_headers = analyze_headers

    def verify(
        self,
        response: Response,
        **kwargs: Any,
    ) -> ResponseVerification:
        """`**kwargs` will be delegated to descriptions."""
        status_code = self._verify_status_code(response.status_code, **kwargs)

        try:
            headers = self._verify_headers(response.headers, **kwargs)
        except Exception as error:
            headers = Verification.of_error(error)

        body = Verification.skipped()
        if self._body_description:
            body = self._body_description.verify(response.body, **kwargs)

        status = merge_statuses(
            status_code.status,
            headers.status,
            body.status,
        )
        return ResponseVerification(
            response_id=response.id,
            status=status,
            status_code=status_code,
            headers=headers,
            body=body,
        )

    @property
    def status_code_predicates(self) -> List[Predicate]:
        return self._status_code_predicates

    @property
    def headers_descriptions(self) -> List[Description]:
        return self._headers_descriptions

    @property
    def body_description(self) -> Optional[BodyDescription]:
        return self._body_description

    def _verify_status_code(
        self,
        code: int,
        **kwargs: Any,
    ) -> Verification:
        return collect(
            predicate.verify(code, **kwargs)
            for predicate in self._status_code_predicates
        )

    def _verify_headers(
        self,
        headers: Mapping[str, str],
        **kwargs: Any,
    ) -> Verification:
        analyzer = self._analyze_headers(headers)
        return collect(
            description.verify(analyzer, **kwargs)
            for description in self._headers_descriptions
        )
