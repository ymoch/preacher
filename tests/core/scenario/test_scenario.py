from concurrent.futures import Executor, Future
from unittest.mock import ANY, MagicMock, patch, sentinel

from pytest import fixture, mark, raises

from preacher.core.scenario.scenario import (
    Scenario,
    ScenarioTask,
    ScenarioResult,
)
from preacher.core.scenario.description import Description
from preacher.core.scenario.status import Status, StatusedSequence
from preacher.core.scenario.util.concurrency import CasesTask
from preacher.core.scenario.verification import Verification

PACKAGE = 'preacher.core.scenario.scenario'


def submit(func, *args, **kwargs) -> Future:
    future: Future = Future()
    future.set_result(func(*args, **kwargs))
    return future


@fixture
def executor():
    executor = MagicMock(Executor)
    executor.submit = MagicMock(side_effect=submit)
    return executor


def test_not_implemented():
    class _IncompleteScenario(ScenarioTask):
        def result(self) -> ScenarioResult:
            return super().result()

    with raises(NotImplementedError):
        _IncompleteScenario().result()


def test_given_unstable_condition():
    pass


def test_given_failing_condition():
    condition_verifications = [
        MagicMock(Verification, status=Status.SUCCESS),
        MagicMock(Verification, status=Status.FAILURE),
        MagicMock(Verification, status=Status.UNSTABLE),
    ]
    conditions = [
        MagicMock(Description, verify=MagicMock(return_value=verification))
        for verification in condition_verifications
    ]
    subscenario = MagicMock(Scenario)

    scenario = Scenario(
        label=sentinel.label,
        conditions=conditions,
        cases=sentinel.cases,
        subscenarios=[subscenario],
    )
    with patch(
        f'{PACKAGE}.OrderedCasesTask'
    ) as ordered_cases_task_ctor, patch(
        f'{PACKAGE}.UnorderedCasesTask'
    ) as unordered_cases_task_ctor:
        result = scenario.submit(executor).result()

    assert result.label is sentinel.label
    assert result.conditions.children == condition_verifications
    assert not result.cases
    assert not result.subscenarios

    ordered_cases_task_ctor.assert_not_called()
    unordered_cases_task_ctor.assert_not_called()
    subscenario.submit.assert_not_called()


def test_given_default_scenario(executor):
    case_results = MagicMock(StatusedSequence, status=Status.SKIPPED)
    cases_task = MagicMock(CasesTask)
    cases_task.result = MagicMock(return_value=case_results)

    scenario = Scenario()
    with patch(
        target=f'{PACKAGE}.OrderedCasesTask',
        return_value=cases_task,
    ) as cases_task_ctor:
        result = scenario.submit(executor).result()

    assert result.label is None
    assert result.status is Status.SKIPPED
    assert result.conditions.status is Status.SKIPPED
    assert result.cases is case_results
    assert result.subscenarios.status is Status.SKIPPED

    cases_task_ctor.assert_called_once_with(
        executor,
        [],
        base_url='',
        retry=0,
        delay=0.1,
        timeout=None,
        listener=ANY,
    )
    cases_task.result.assert_called_once_with()
    executor.submit.assert_not_called()


@mark.parametrize('cases_status, subscenario_status, expected_status', [
    (Status.SUCCESS, Status.UNSTABLE, Status.UNSTABLE),
    (Status.UNSTABLE, Status.FAILURE, Status.FAILURE),
])
@patch(f'{PACKAGE}.ScenarioContext', return_value=sentinel.context)
@patch(f'{PACKAGE}.analyze_context', return_value=sentinel.context_analyzer)
def test_given_filled_scenarios(
    analyze_context,
    context_ctor,
    executor,
    cases_status,
    subscenario_status,
    expected_status,
):
    condition_result = MagicMock(Verification, status=Status.SUCCESS)
    condition = MagicMock(Description)
    condition.verify = MagicMock(return_value=condition_result)

    case_results = MagicMock(StatusedSequence, status=cases_status)
    cases_task = MagicMock(CasesTask)
    cases_task.result = MagicMock(return_value=case_results)

    subscenario_result = MagicMock(ScenarioResult, status=subscenario_status)
    subscenario_task = MagicMock(ScenarioTask)
    subscenario_task.result = MagicMock(return_value=subscenario_result)
    subscenario = MagicMock(Scenario)
    subscenario.submit = MagicMock(return_value=subscenario_task)

    sentinel.context.starts = sentinel.starts

    scenario = Scenario(
        ordered=False,
        conditions=[condition],
        cases=sentinel.cases,
        subscenarios=[subscenario]
    )

    with patch(
        target=f'{PACKAGE}.UnorderedCasesTask',
        return_value=cases_task,
    ) as cases_task_ctor:
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
    assert result.cases is case_results
    assert result.subscenarios[0] is subscenario_result

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
    cases_task_ctor.assert_called_once_with(
        executor,
        sentinel.cases,
        base_url='base-url',
        retry=2,
        delay=0.5,
        timeout=1.0,
        listener=sentinel.listener,
    )
    cases_task.result.assert_called_once_with()
    subscenario.submit.assert_called_once_with(
        executor,
        base_url='base-url',
        retry=2,
        delay=0.5,
        timeout=1.0,
        listener=sentinel.listener,
    )
    subscenario_task.result.assert_called_once_with()
