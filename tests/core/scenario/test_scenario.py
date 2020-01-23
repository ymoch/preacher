from concurrent.futures import Executor, Future, ThreadPoolExecutor
from unittest.mock import ANY, MagicMock, patch, sentinel

from pytest import raises, fixture

from preacher.core.scenario.case import Case
from preacher.core.scenario.description import Description
from preacher.core.scenario import Scenario, ScenarioTask, ScenarioResult
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


@patch(f'{PACKAGE}.ScenarioContext', return_value=sentinel.context)
@patch(f'{PACKAGE}.analyze_context', return_value=sentinel.context_analyzer)
def test_given_subscenarios(analyze_context, context_ctor):
    condition1 = MagicMock(Description, verify=MagicMock(
        return_value=Verification.succeed()
    ))
    condition2 = MagicMock(Description, verify=MagicMock(
        return_value=Verification(status=Status.UNSTABLE)
    ))
    condition3 = MagicMock(Description, verify=MagicMock(
        return_value=Verification.succeed()
    ))
    condition4 = MagicMock(Description, verify=MagicMock(
        return_value=Verification(status=Status.FAILURE)
    ))
    condition5 = MagicMock(Description, verify=MagicMock(
        return_value=Verification(status=Status.UNSTABLE)
    ))

    sentinel.result1.status = Status.SUCCESS
    case1 = MagicMock(Case, run=MagicMock(return_value=sentinel.result1))

    sentinel.subresult1.status = Status.UNSTABLE
    subcase1 = MagicMock(Case)
    subcase1.run.return_value = sentinel.subresult1
    sentinel.subresult2.status = Status.SUCCESS
    subcase2 = MagicMock(Case)
    subcase2.run.return_value = sentinel.subresult2
    sentinel.subresult3.status = Status.FAILURE
    subcase3 = MagicMock(Case)
    subcase3.run.return_value = sentinel.subresult3
    sentinel.subresult4.status = Status.SUCCESS
    subcase4 = MagicMock(Case)
    subcase4.run.return_value = sentinel.subresult4
    sentinel.subresult5.status = Status.SUCCESS
    subcase5 = MagicMock(Case)
    subcase5.run.return_value = sentinel.subresult5

    subscenario1 = Scenario(cases=[subcase1])
    subscenario2 = Scenario(cases=[subcase2, subcase3])
    subscenario3 = Scenario(
        conditions=[condition2, condition3],
        cases=[subcase4],
    )
    subscenario4 = Scenario(
        conditions=[condition4, condition5],
        cases=[subcase5],
    )
    scenario = Scenario(
        conditions=[condition1],
        cases=[case1],
        subscenarios=[subscenario1, subscenario2, subscenario3, subscenario4],
    )

    sentinel.context.starts = sentinel.starts

    result = scenario.run(
        base_url='base-url',
        retry=2,
        delay=0.5,
        timeout=1.0,
        listener=sentinel.listener,
    )
    assert result.status == Status.FAILURE
    assert result.subscenarios[0].status == Status.UNSTABLE
    assert result.subscenarios[1].status == Status.FAILURE
    assert result.subscenarios[2].status == Status.SKIPPED
    assert (
        result.subscenarios[2].conditions.children[0].status == Status.UNSTABLE
    )
    assert (
        result.subscenarios[2].conditions.children[1].status == Status.SUCCESS
    )
    assert result.subscenarios[3].status == Status.FAILURE
    assert (
        result.subscenarios[3].conditions.children[0].status == Status.FAILURE
    )
    assert (
        result.subscenarios[3].conditions.children[1].status == Status.UNSTABLE
    )

    context_ctor.assert_called_with(
        base_url='base-url',
        retry=2,
        delay=0.5,
        timeout=1.0,
    )
    analyze_context.assert_called_with(sentinel.context)
    condition1.verify.assert_called_with(
        sentinel.context_analyzer,
        origin_datetime=sentinel.starts,
    )
    for case in [subcase1, subcase2, subcase3]:
        case.run.assert_called_once_with(
            base_url='base-url',
            retry=2,
            delay=0.5,
            timeout=1.0,
            listener=sentinel.listener,
        )
    for case in [subcase4, subcase5]:
        case.run.assert_not_called()
