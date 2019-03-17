"""Scenario."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import List, Optional

from .description import Description
from .request import Request
from .verification import (
    Status,
    Verification,
    merge_statuses,
)


@dataclass
class ResponseScenarioVerification:
    status: Status
    body: Verification


class ResponseScenario:
    def __init__(
        self: ResponseScenario,
        body_descriptions: List[Description],
    ) -> None:
        self._body_descriptions = body_descriptions

    def __call__(
        self: ResponseScenario,
        body: str,
    ) -> ResponseScenarioVerification:
        try:
            body_verification = self._verify_body(body)
        except Exception as error:
            body_verification = Verification.of_error(error)

        status = body_verification.status
        return ResponseScenarioVerification(
            status=status,
            body=body_verification,
        )

    @property
    def body_descriptions(self: ResponseScenario) -> List[Description]:
        return self._body_descriptions

    def _verify_body(self: ResponseScenario, body: str) -> Verification:
        data = json.loads(body)
        verifications = [
            describe(data) for describe in self._body_descriptions
        ]
        status = merge_statuses(v.status for v in verifications)
        return Verification(status=status, children=verifications)


@dataclass
class ScenarioVerification:
    status: Status
    request: Verification
    response_scenario: Optional[ResponseScenarioVerification] = None


class Scenario:
    def __init__(
        self: Scenario,
        request: Request,
        response_scenario: ResponseScenario,
    ) -> None:
        self._request = request
        self._response_scenario = response_scenario

    def __call__(self: Scenario, base_url: str) -> ScenarioVerification:
        try:
            response = self._request(base_url)
        except Exception as error:
            return ScenarioVerification(
                status=Status.FAILURE,
                request=Verification.of_error(error),
            )
        request_verification = Verification.succeed()

        response_scenario_verification = self._response_scenario(
            body=response.body,
        )

        status = merge_statuses([
            request_verification.status,
            response_scenario_verification.status,
        ])
        return ScenarioVerification(
            status=status,
            request=request_verification,
            response_scenario=response_scenario_verification,
        )

    @property
    def request(self: Scenario) -> Request:
        return self._request

    @property
    def response_scenario(self: Scenario) -> ResponseScenario:
        return self._response_scenario
