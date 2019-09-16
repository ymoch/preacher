"""Response descriptions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, List, Mapping, Optional

from .analysis import Analyzer, JsonAnalyzer
from .body_description import BodyDescription
from .description import Description, Predicate
from .status import Status, merge_statuses
from .verification import Verification


@dataclass(frozen=True)
class ResponseVerification:
    status: Status
    status_code: Verification
    headers: Verification
    body: Verification


class ResponseDescription:

    def __init__(
        self,
        status_code_predicates: List[Predicate] = [],
        headers_descriptions: List[Description] = [],
        body_description: Optional[BodyDescription] = None,
        analyze_headers:
            Callable[[Mapping[str, str]], Analyzer] = JsonAnalyzer,
    ):
        self._status_code_predicates = status_code_predicates
        self._headers_descriptions = headers_descriptions
        self._body_description = body_description
        self._analyze_headers = analyze_headers

    def verify(
        self,
        status_code: int,
        headers: Mapping[str, str],
        body: str,
        **kwargs: Any,
    ) -> ResponseVerification:
        """`**kwargs` will be delegated to descriptions."""
        status_code_verification = self._verify_status_code(
            status_code,
            **kwargs,
        )

        try:
            headers_verification = self._verify_headers(headers, **kwargs)
        except Exception as error:
            headers_verification = Verification.of_error(error)

        body_verification = Verification.skipped()
        if self._body_description:
            body_verification = self._body_description.verify(body, **kwargs)

        status = merge_statuses(
            status_code_verification.status,
            headers_verification.status,
            body_verification.status,
        )
        return ResponseVerification(
            status=status,
            status_code=status_code_verification,
            headers=headers_verification,
            body=body_verification,
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
        children = [
            predicate(code, **kwargs)
            for predicate in self._status_code_predicates
        ]
        status = merge_statuses(v.status for v in children)
        return Verification(status=status, children=children)

    def _verify_headers(
        self,
        header: Mapping[str, str],
        **kwargs: Any,
    ) -> Verification:
        analyzer = self._analyze_headers(header)
        verifications = [
            describe(analyzer, **kwargs)
            for describe in self._headers_descriptions
        ]
        status = merge_statuses(v.status for v in verifications)
        return Verification(status=status, children=verifications)
