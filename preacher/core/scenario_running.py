"""Scenario running helpers."""

from .scenario import Scenario, ScenarioResult


def run_scenario(
    scenario: Scenario,
    base_url: str,
    retry: int = 0,
) -> ScenarioResult:
    return scenario.run(base_url=base_url, retry=retry)
