from concurrent.futures import Executor, Future
from unittest.mock import ANY, Mock, NonCallableMock, sentinel

from pytest import fixture, mark

from preacher.core.scenario.case_runner import CaseRunner
from preacher.core.scenario.scenario import Scenario, ScenarioContext
from preacher.core.scenario.scenario_result import ScenarioResult
from preacher.core.scenario.scenario_task import ScenarioTask
from preacher.core.scenario.util.concurrency import CasesTask
from preacher.core.status import Status, StatusedList
from preacher.core.value import ValueContext
from preacher.core.verification import Description, Verification

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


@mark.parametrize('statuses, expected_status', [
    ([Status.SKIPPED, Status.UNSTABLE, Status.SUCCESS], Status.SKIPPED),
    ([Status.SUCCESS, Status.FAILURE, Status.UNSTABLE], Status.FAILURE),
])
def test_given_not_satisfied_conditions(mocker, statuses, expected_status):
    context = ScenarioContext(starts=sentinel.starts)
    context_ctor = mocker.patch(f'{PKG}.ScenarioContext', return_value=context)

    analyze_context = mocker.patch(f'{PKG}.analyze_data_obj')
    analyze_context.return_value = sentinel.context_analyzer

    ordered_cases_task_ctor = mocker.patch(f'{PKG}.OrderedCasesTask')
    unordered_cases_task_ctor = mocker.patch(f'{PKG}.UnorderedCasesTask')

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
    case_runner = NonCallableMock(CaseRunner, base_url=sentinel.base_url)
    result = scenario.submit(executor, case_runner).result()

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
            ValueContext(origin_datetime=sentinel.starts),
        )

    context_ctor.assert_called_once_with(base_url=sentinel.base_url)
    analyze_context.assert_called_once_with(context)
    ordered_cases_task_ctor.assert_not_called()
    unordered_cases_task_ctor.assert_not_called()
    subscenario.submit.assert_not_called()


def test_unordered(executor, mocker):
    # Also tests successful conditions.
    condition = NonCallableMock(Description)
    condition.verify.return_value = Verification(Status.SUCCESS)

    results = NonCallableMock(StatusedList, status=Status.SKIPPED)
    cases_task = NonCallableMock(CasesTask)
    cases_task.result.return_value = results
    cases_task_ctor = mocker.patch(f'{PKG}.UnorderedCasesTask', return_value=cases_task)

    scenario = Scenario(conditions=[condition], ordered=False)
    case_runner = NonCallableMock(CaseRunner, base_url=sentinel.base_url)
    result = scenario.submit(executor, case_runner).result()

    assert result.label is None
    assert result.status is Status.SKIPPED
    assert result.conditions.status is Status.SUCCESS
    assert result.cases is results
    assert result.subscenarios.status is Status.SKIPPED
    assert not result.subscenarios.items

    condition.verify.assert_called_once()
    cases_task_ctor.assert_called_once_with(executor, case_runner, [], ANY)
    cases_task.result.assert_called_once_with()
    executor.submit.assert_not_called()


@mark.parametrize('cases_status, subscenario_status, expected_status', [
    (Status.SUCCESS, Status.UNSTABLE, Status.UNSTABLE),
    (Status.UNSTABLE, Status.FAILURE, Status.FAILURE),
])
def test_ordered(
    executor,
    cases_status,
    subscenario_status,
    expected_status,
    mocker,
):
    cases_result = NonCallableMock(StatusedList, status=cases_status)
    cases_task = NonCallableMock(CasesTask)
    cases_task.result.return_value = cases_result
    cases_task_ctor = mocker.patch(f'{PKG}.OrderedCasesTask')
    cases_task_ctor.return_value = cases_task

    subscenario_result = NonCallableMock(ScenarioResult)
    subscenario_result.status = subscenario_status
    subscenario_task = NonCallableMock(ScenarioTask)
    subscenario_task.result.return_value = subscenario_result
    subscenario = NonCallableMock(Scenario)
    subscenario.submit.return_value = subscenario_task

    sentinel.context.starts = sentinel.starts

    scenario = Scenario(cases=sentinel.cases, subscenarios=[subscenario])

    case_runner = NonCallableMock(CaseRunner, base_url=sentinel.base_url)
    result = scenario.submit(executor, case_runner, sentinel.listener).result()

    assert result.status == expected_status
    assert result.conditions.status is Status.SKIPPED
    assert result.cases is cases_result
    assert result.subscenarios.items[0] is subscenario_result

    cases_task_ctor.assert_called_once_with(
        executor,
        case_runner,
        sentinel.cases,
        sentinel.listener,
    )
    cases_task.result.assert_called_once_with()
    subscenario.submit.assert_called_once_with(executor, case_runner, sentinel.listener)
    subscenario_task.result.assert_called_once_with()
