from unittest.mock import NonCallableMock, sentinel

from pytest import mark, raises

from preacher.core.scenario.scenario_result import ScenarioResult
from preacher.core.scenario.scenario_task import ScenarioTask
from preacher.core.scenario.scenario_task import StaticScenarioTask, RunningScenarioTask
from preacher.core.scenario.util.concurrency import CasesTask
from preacher.core.status import Status, StatusedList


def test_scenario_task_interface():
    class _IncompleteScenarioTask(ScenarioTask):
        def result(self) -> ScenarioResult:
            return super().result()

    with raises(NotImplementedError):
        _IncompleteScenarioTask().result()


def test_static_scenario_task():
    task = StaticScenarioTask(sentinel.result)
    assert task.result() is sentinel.result


def test_running_scenario_task_empty():
    cases_result = NonCallableMock(StatusedList, status=Status.SKIPPED)
    cases = NonCallableMock(CasesTask)
    cases.result.return_value = cases_result

    task = RunningScenarioTask(
        label=sentinel.label,
        conditions=sentinel.conditions,
        cases=cases,
        subscenarios=[],
    )
    result = task.result()

    assert result.label is sentinel.label
    assert result.status is Status.SKIPPED
    assert result.message is None
    assert result.conditions is sentinel.conditions
    assert result.cases is cases_result
    assert not result.subscenarios.items

    cases.result.assert_called_once_with()


@mark.parametrize('cases_status, subscenario_status, expected_status', [
    (Status.SUCCESS, Status.UNSTABLE, Status.UNSTABLE),
    (Status.UNSTABLE, Status.FAILURE, Status.FAILURE),
])
def test_running_scenario_task_filled(cases_status, subscenario_status, expected_status):
    cases_result = NonCallableMock(StatusedList, status=cases_status)
    cases = NonCallableMock(CasesTask)
    cases.result.return_value = cases_result

    subscenario = NonCallableMock(ScenarioTask)
    subscenario_result = ScenarioResult(status=subscenario_status)
    subscenario.result.return_value = subscenario_result

    task = RunningScenarioTask(
        label=sentinel.label,
        conditions=sentinel.conditions,
        cases=cases,
        subscenarios=[subscenario],
    )
    result = task.result()

    assert result.label is sentinel.label
    assert result.status is expected_status
    assert result.message is None
    assert result.conditions is sentinel.conditions
    assert result.cases is cases_result
    assert len(result.subscenarios.items) == 1
    assert result.subscenarios.items[0] is subscenario_result
