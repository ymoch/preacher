"""Scenario."""

from __future__ import annotations

import json
from typing import List

from .description import Description
from .request import Request
from .verification import (
    Verification,
    ResponseVerification,
    merge_statuses,
)


class ResponseScenario:
    def __init__(
        self: ResponseScenario,
        body_descriptions: List[Description],
    ) -> None:
        self._body_descriptions = body_descriptions

    def __call__(
        self: ResponseScenario,
        body: bytes,
    ) -> ResponseVerification:
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


class Scenario:
    def __init__(
        self: Scenario,
        request: Request,
        response_scenario: ResponseScenario,
    ) -> None:
        self._request = request
        self._response_scenario = response_scenario

    def __call__(self: Scenario, base_url: str) -> None:
        try:
            self._request(base_url)
        except Exception as error:
            Verification.of_error(error)
