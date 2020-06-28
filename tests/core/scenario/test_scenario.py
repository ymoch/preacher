from concurrent.futures import Executor, Future
from unittest.mock import ANY, Mock, NonCallableMock, sentinel

from pytest import fixture, mark, raises

from preacher.core.scenario.description import Description
from preacher.core.scenario.scenario import (
    Scenario,
    ScenarioTask,
    ScenarioResult, ScenarioContext,
)
from preacher.core.scenario.status import Status, StatusedList
from preacher.core.scenario.util.concurrency import CasesTask
from preacher.core.scenario.verification import Verification

PKG = 'preacher.core.scenario.scenario'


@fixture
def executor():
    def _submit(func, *args, **kwargs) -> Future:
        future: Future = Future()
        future.set_result(func(*args, **kwargs))
        return future

    executor = NonCallableMock(Executor)
    executor.submit.side_effect = _submit
    return executor


def test_scenario_task_interface():
    class _IncompleteScenarioTask(ScenarioTask):
        def result(self) -> ScenarioResult:
            return super().result()

    with raises(NotImplementedError):
        _IncompleteScenarioTask().result()


@mark.parametrize('statuses, expected_status', [
    ([Status.SKIPPED, Status.UNSTABLE, Status.SUCCESS], Status.SKIPPED),
    ([Status.SUCCESS, Status.FAILURE, Status.UNSTABLE], Status.FAILURE),
])
def test_conditions_not_satisfied(mocker, statuses, expected_status):
    context_ctor = mocker.patch(f'{PKG}.ScenarioContext')
    context_ctor.return_value = ScenarioContext(starts=sentinel.starts)

    analyze_context = mocker.patch(f'{PKG}.analyze_data_obj')
    analyze_context.return_value = sentinel.context_analyzer

    ordered_task_ctor = mocker.patch(f'{PKG}.OrderedCasesTask')
    unordered_task_ctor = mocker.patch(f'{PKG}.UnorderedCasesTask')

    verifications = [Verification(status) for status in statuses]
    conditions = [
        NonCallableMock(Description, verify=Mock(return_value=v))
        for v in verifications
    ]
    subscenario = NonCallableMock(Scenario)

    scenario = Scenario(
        label=sentinel.label,
        conditions=conditions,
        cases=sentinel.cases,
        subscenarios=[subscenario],
    )
    result = scenario.submit(executor).result()

    assert result.label is sentinel.label
    assert result.status is expected_status
    assert result.conditions.children == verifications
    assert result.cases.status is Status.SKIPPED
    assert not result.cases.items
    assert result.subscenarios.status is Status.SKIPPED
    assert not result.subscenarios.items

    for condition in conditions:
        condition.verify.assert_called_once_with(
            sentinel.context_analyzer,
            origin_datetime=sentinel.starts,
        )

    ordered_task_ctor.assert_not_called()
    unordered_task_ctor.assert_not_called()
    subscenario.submit.assert_not_called()


def test_given_default_scenario(executor, mocker):
    results = NonCallableMock(StatusedList, status=Status.SKIPPED)
    task = NonCallableMock(CasesTask)
    task.result.return_value = results
    task_ctor = mocker.patch(f'{PKG}.OrderedCasesTask', return_value=task)

    scenario = Scenario()
    result = scenario.submit(executor).result()

    assert result.label is None
    assert result.status is Status.SKIPPED
    assert result.conditions.status is Status.SKIPPED
    assert result.cases is results
    assert result.subscenarios.status is Status.SKIPPED
    assert not result.subscenarios.items

    task_ctor.assert_called_once_with(
        executor,
        [],
        base_url='',
        retry=0,
        delay=0.1,
        timeout=None,
        listener=ANY,
    )

    task.result.assert_called_once_with()
    executor.submit.assert_not_called()


@mark.parametrize('cases_status, subscenario_status, expected_status', [
    (Status.SUCCESS, Status.UNSTABLE, Status.UNSTABLE),
    (Status.UNSTABLE, Status.FAILURE, Status.FAILURE),
])
def test_given_filled_scenarios(
    executor,
    cases_status,
    subscenario_status,
    expected_status,
    mocker,
):
    context_ctor = mocker.patch(f'{PKG}.ScenarioContext')
    context_ctor.return_value = sentinel.context

    analyze_context = mocker.patch(f'{PKG}.analyze_data_obj')
    analyze_context.return_value = sentinel.context_analyzer

    condition_result = NonCallableMock(Verification, status=Status.SUCCESS)
    condition = NonCallableMock(Description)
    condition.verify.return_value = condition_result

    results = NonCallableMock(StatusedList, status=cases_status)
    task = NonCallableMock(CasesTask)
    task.result.return_value = results
    task_ctor = mocker.patch(f'{PKG}.UnorderedCasesTask', return_value=task)

    subscenario_result = NonCallableMock(ScenarioResult)
    subscenario_result.status = subscenario_status
    subscenario_task = NonCallableMock(ScenarioTask)
    subscenario_task.result.return_value = subscenario_result
    subscenario = NonCallableMock(Scenario)
    subscenario.submit.return_value = subscenario_task

    sentinel.context.starts = sentinel.starts

    scenario = Scenario(
        ordered=False,
        conditions=[condition],
        cases=sentinel.cases,
        subscenarios=[subscenario]
    )

    result = scenario.submit(
        executor,
        base_url='base-url',
        retry=2,
        delay=0.5,
        timeout=1.0,
        listener=sentinel.listener,
    ).result()

    assert result.status == expected_status
    assert result.conditions.children[0] is condition_result
    assert result.cases is results
    assert result.subscenarios.items[0] is subscenario_result

    context_ctor.assert_called_with(
        base_url='base-url',
        retry=2,
        delay=0.5,
        timeout=1.0,
    )
    condition.verify.assert_called_once_with(
        sentinel.context_analyzer,
        origin_datetime=sentinel.starts,
    )
    analyze_context.assert_called_with(sentinel.context)
    task_ctor.assert_called_once_with(
        executor,
        sentinel.cases,
        base_url='base-url',
        retry=2,
        delay=0.5,
        timeout=1.0,
        listener=sentinel.listener,
    )
    task.result.assert_called_once_with()
    subscenario.submit.assert_called_once_with(
        executor,
        base_url='base-url',
        retry=2,
        delay=0.5,
        timeout=1.0,
        listener=sentinel.listener,
    )
    subscenario_task.result.assert_called_once_with()
