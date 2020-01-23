from concurrent.futures import Executor, Future, ThreadPoolExecutor
from unittest.mock import ANY, MagicMock, patch, sentinel

from pytest import raises, fixture

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


def test_given_an_empty_scenario():
    scenario = Scenario(label=None, cases=[])
    with ThreadPoolExecutor(1) as executor:
        result = scenario.submit(executor).result()
    assert result.label is None
    assert result.status == Status.SKIPPED
    assert list(result.cases) == []


@patch(f'{PACKAGE}.OrderedCasesTask')
@patch(f'{PACKAGE}.ScenarioContext', return_value=sentinel.context)
@patch(f'{PACKAGE}.analyze_context', return_value=sentinel.context_analyzer)
def test_given_a_filled_scenario(
    analyze_context,
    context_ctor,
    cases_task_ctor,
    executor,
):
    case_results = StatusedSequence(
        status=Status.UNSTABLE,
        items=[sentinel.case_result],
    )
    cases_task = MagicMock(CasesTask)
    cases_task.result = MagicMock(return_value=case_results)
    cases_task_ctor.return_value = cases_task

    scenario = Scenario(label='label', cases=sentinel.cases)
    result = scenario.submit(executor).result()
    assert result.label == 'label'
    assert result.status == Status.UNSTABLE
    assert result.cases is case_results

    context_ctor.assert_called_once_with(
        base_url='',
        retry=0,
        delay=0.1,
        timeout=None,
    )
    analyze_context.assert_called_once_with(sentinel.context)
    cases_task_ctor.assert_called_once_with(
        executor,
        sentinel.cases,
        base_url='',
        retry=0,
        delay=0.1,
        timeout=None,
        listener=ANY,
    )
    cases_task.result.assert_called_once_with()


@patch(f'{PACKAGE}.UnorderedCasesTask')
@patch(f'{PACKAGE}.ScenarioContext', return_value=sentinel.context)
@patch(f'{PACKAGE}.analyze_context', return_value=sentinel.context_analyzer)
def test_given_subscenarios(
    analyze_context,
    context_ctor,
    cases_task_ctor,
    executor,
):
    subscenario_result = MagicMock(ScenarioResult, status=Status.FAILURE)
    subscenario_task = MagicMock(ScenarioTask)
    subscenario_task.result = MagicMock(return_value=subscenario_result)
    subscenario = MagicMock(Scenario)
    subscenario.submit = MagicMock(return_value=subscenario_task)

    case_results = StatusedSequence(
        status=Status.UNSTABLE,
        items=[sentinel.case_result],
    )
    cases_task = MagicMock(CasesTask)
    cases_task.result = MagicMock(return_value=case_results)
    cases_task_ctor.return_value = cases_task

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
    assert result.status == Status.FAILURE
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
