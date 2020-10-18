from pytest import raises

from preacher.core.scenario.scenario_task import ScenarioTask, ScenarioResult


def test_scenario_task_interface():
    class _IncompleteScenarioTask(ScenarioTask):
        def result(self) -> ScenarioResult:
            return super().result()

    with raises(NotImplementedError):
        _IncompleteScenarioTask().result()
