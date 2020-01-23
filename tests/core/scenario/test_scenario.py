from concurrent.futures import Executor, Future
from unittest.mock import MagicMock, patch, sentinel

from pytest import raises, fixture, mark

from preacher.core.scenario import Scenario, ScenarioTask, ScenarioResult
from preacher.core.scenario.status import Status, StatusedSequence
from preacher.core.scenario.util.concurrency import CasesTask

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


@mark.parametrize('case_status, subscenario_status, expected_status', [
    (Status.SUCCESS, Status.UNSTABLE, Status.UNSTABLE),
    (Status.UNSTABLE, Status.FAILURE, Status.FAILURE),
])
@patch(f'{PACKAGE}.UnorderedCasesTask')
@patch(f'{PACKAGE}.ScenarioContext', return_value=sentinel.context)
@patch(f'{PACKAGE}.analyze_context', return_value=sentinel.context_analyzer)
def test_given_filled_scenarios(
    analyze_context,
    context_ctor,
    cases_task_ctor,
    executor,
    case_status,
    subscenario_status,
    expected_status,
):
    case_results = StatusedSequence(
        status=case_status,
        items=[sentinel.case_result],
    )
    cases_task = MagicMock(CasesTask)
    cases_task.result = MagicMock(return_value=case_results)
    cases_task_ctor.return_value = cases_task

    subscenario_result = MagicMock(ScenarioResult, status=subscenario_status)
    subscenario_task = MagicMock(ScenarioTask)
    subscenario_task.result = MagicMock(return_value=subscenario_result)
    subscenario = MagicMock(Scenario)
    subscenario.submit = MagicMock(return_value=subscenario_task)

    sentinel.context.starts = sentinel.starts

    scenario = Scenario(
        ordered=False,
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
    assert result.cases is case_results
    assert result.subscenarios[0] is subscenario_result

    context_ctor.assert_called_with(
        base_url='base-url',
        retry=2,
        delay=0.5,
        timeout=1.0,
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
