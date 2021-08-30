from unittest.mock import Mock, NonCallableMock, call, sentinel

from pytest import mark

from preacher.core.scenario.case_runner import CaseRunner
from preacher.core.scenario.scenario import Scenario
from preacher.core.scenario.scenario_runner import ScenarioRunner
from preacher.core.status import Status
from preacher.core.value import ValueContext
from preacher.core.verification import Description, Verification

PKG = "preacher.core.scenario.scenario_runner"


@mark.parametrize(
    ("statuses", "expected_status"),
    (
        ([Status.SKIPPED, Status.UNSTABLE, Status.SUCCESS], Status.SKIPPED),
        ([Status.SUCCESS, Status.FAILURE, Status.UNSTABLE], Status.FAILURE),
    ),
)
def test_given_not_satisfied_conditions(mocker, statuses, expected_status):
    mocker.patch(f"{PKG}.now", return_value=sentinel.starts)

    analyze_context = mocker.patch(f"{PKG}.MappingAnalyzer")
    analyze_context.return_value = sentinel.context_analyzer

    ordered_cases_task_ctor = mocker.patch(f"{PKG}.OrderedCasesTask")
    unordered_cases_task_ctor = mocker.patch(f"{PKG}.UnorderedCasesTask")
    task_ctor = mocker.patch(f"{PKG}.StaticScenarioTask", return_value=sentinel.task)

    verifications = [Verification(status) for status in statuses]
    conditions = [NonCallableMock(Description, verify=Mock(return_value=v)) for v in verifications]

    scenario = Scenario(
        label=sentinel.label,
        conditions=conditions,
        cases=sentinel.cases,
        subscenarios=[sentinel.subscenario],
    )
    case_runner = NonCallableMock(CaseRunner, base_url=sentinel.base_url)
    runner = ScenarioRunner(executor=sentinel.executor, case_runner=case_runner)
    task = runner.submit(scenario)
    assert task is sentinel.task

    result = task_ctor.call_args[0][0]
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

    analyze_context.assert_called_once_with(
        {"starts": sentinel.starts, "base_url": sentinel.base_url}
    )
    ordered_cases_task_ctor.assert_not_called()
    unordered_cases_task_ctor.assert_not_called()


def test_unordered(mocker):
    # Also tests successful conditions.
    condition_verification = Verification(Status.SUCCESS)
    condition = NonCallableMock(Description)
    condition.verify.return_value = condition_verification

    cases_task_ctor = mocker.patch(f"{PKG}.UnorderedCasesTask", return_value=sentinel.cases_task)
    task_ctor = mocker.patch(f"{PKG}.RunningScenarioTask", return_value=sentinel.task)

    scenario = Scenario(conditions=[condition], ordered=False)
    case_runner = NonCallableMock(CaseRunner, base_url=sentinel.base_url)
    runner = ScenarioRunner(executor=sentinel.executor, case_runner=case_runner)
    task = runner.submit(scenario)
    assert task is sentinel.task

    task_ctor.assert_called_once_with(
        label=None,
        conditions=Verification(status=Status.SUCCESS, children=[condition_verification]),
        cases=sentinel.cases_task,
        subscenarios=[],
    )

    condition.verify.assert_called_once()
    cases_task_ctor.assert_called_once_with(sentinel.executor, case_runner, [])


def test_ordered(mocker):
    cases_task_ctor = mocker.patch(f"{PKG}.OrderedCasesTask", return_value=sentinel.cases_task)
    task_ctor = mocker.patch(f"{PKG}.RunningScenarioTask", return_value=sentinel.task)

    sentinel.context.starts = sentinel.starts

    subscenario = Scenario(label=sentinel.subscenario_label)
    scenario = Scenario(label=sentinel.label, cases=sentinel.cases, subscenarios=[subscenario])

    case_runner = NonCallableMock(CaseRunner, base_url=sentinel.base_url)
    runner = ScenarioRunner(executor=sentinel.executor, case_runner=case_runner)
    task = runner.submit(scenario)
    assert task is sentinel.task

    cases_task_ctor.assert_has_calls(
        [
            call(sentinel.executor, case_runner, sentinel.cases),
            call(sentinel.executor, case_runner, []),
        ]
    )
    task_ctor.assert_has_calls(
        [
            call(
                label=sentinel.subscenario_label,
                conditions=Verification.collect([]),
                cases=sentinel.cases_task,
                subscenarios=[],
            ),
            call(
                label=sentinel.label,
                conditions=Verification(status=Status.SKIPPED, children=[]),
                cases=sentinel.cases_task,
                subscenarios=[sentinel.task],
            ),
        ]
    )
