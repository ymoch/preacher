"""Response descriptions."""

import json
from dataclasses import dataclass
from typing import Any, List

from .description import Description, Predicate
from .status import Status, merge_statuses
from .verification import Verification


@dataclass(frozen=True)
class ResponseVerification:
    status: Status
    status_code: Verification
    body: Verification


class ResponseDescription:

    def __init__(
        self,
        status_code_predicates: List[Predicate],
        body_descriptions: List[Description],
    ):
        self._status_code_predicates = status_code_predicates
        self._body_descriptions = body_descriptions

    def __call__(
        self,
        status_code: int,
        body: str,
        **kwargs: Any,
    ) -> ResponseVerification:
        """`**kwargs` will be delegated to descriptions."""
        status_code_verification = self._verify_status_code(
            status_code,
            **kwargs,
        )
        try:
            body_verification = self._verify_body(body, **kwargs)
        except Exception as error:
            body_verification = Verification.of_error(error)

        status = merge_statuses(
            status_code_verification.status,
            body_verification.status,
        )
        return ResponseVerification(
            status=status,
            status_code=status_code_verification,
            body=body_verification,
        )

    @property
    def status_code_predicates(self) -> List[Predicate]:
        return self._status_code_predicates

    @property
    def body_descriptions(self) -> List[Description]:
        return self._body_descriptions

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

    def _verify_body(
        self,
        body: str,
        **kwargs: Any,
    ) -> Verification:
        if not self._body_descriptions:
            return Verification.skipped()

        data = json.loads(body)
        verifications = [
            describe(data, **kwargs)
            for describe in self._body_descriptions
        ]
        status = merge_statuses(v.status for v in verifications)
        return Verification(status=status, children=verifications)
