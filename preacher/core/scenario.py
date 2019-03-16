"""Scenario."""

import json
from typing import List

from .description import Description
from .verification import (
    Verification,
    ResponseVerification,
    merge_statuses,
)


class ResponseScenario:
    def __init__(self, body_descriptions: List[Description]) -> None:
        self._body_descriptions = body_descriptions

    def __call__(self, body: bytes) -> ResponseVerification:
        body_data = json.loads(body.decode('utf-8'))
        body_verifications = [
            describe(body_data) for describe in self._body_descriptions
        ]
        body_status = merge_statuses(v.status for v in body_verifications)

        status = body_status

        return ResponseVerification(
            status=status,
            body=Verification(
                status=body_status,
                children=body_verifications,
            ),
        )
