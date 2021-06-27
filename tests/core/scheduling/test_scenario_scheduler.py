from typing import Iterable, Iterator
from unittest.mock import Mock, NonCallableMock, call, sentinel

from preacher.core.scenario import Scenario, ScenarioRunner, ScenarioResult, ScenarioTask
from preacher.core.scheduling import create_scheduler
from preacher.core.scheduling.listener import Listener
from preacher.core.scheduling.scenario_scheduler import ScenarioScheduler
from preacher.core.status import Status

PKG = 'preacher.core.scheduling.scenario_scheduler'


def test_given_no_scenario():
    scheduler = ScenarioScheduler(sentinel.runner)
    status = scheduler.run([])
    assert status == Status.SKIPPED


def test_given_construction_failure():
    class _Scenarios(Iterable[Scenario]):
        def __init__(self):
            self._count = 0

        def __iter__(self) -> Iterator[Scenario]:
            return self

        def __next__(self) -> Scenario:
            self._count += 1
            if self._count == 2:
                raise Exception("message")
            if self._count > 3:
                raise StopIteration()
            return sentinel.scenario

    def _submit(_: Scenario) -> ScenarioTask:
        result = ScenarioResult(status=Status.SUCCESS)
        task = NonCallableMock(ScenarioTask)
        task.result.return_value = result
        return task

    runner = NonCallableMock(ScenarioRunner)
    runner.submit.side_effect = _submit
    listener = NonCallableMock(Listener)
    scheduler = ScenarioScheduler(runner, listener)
    status = scheduler.run(_Scenarios())
    assert status is Status.FAILURE

    results = [c[0][0] for c in listener.on_scenario.call_args_list]
    assert len(results) == 3

    first_successful = results[0]
    assert first_successful.status is Status.SUCCESS

    construction_failure = results[1]
    assert construction_failure.label == "Not a constructed scenario"
    assert construction_failure.status is Status.FAILURE
    assert construction_failure.message == "Exception: message"

    second_successful = results[2]
    assert second_successful.status is Status.SUCCESS


def test_given_scenarios():
    results = [ScenarioResult(status=Status.UNSTABLE), ScenarioResult(status=Status.FAILURE)]
    tasks = [NonCallableMock(ScenarioTask, result=Mock(return_value=result)) for result in results]
    scenarios = [NonCallableMock(Scenario) for _ in tasks]
    listener = NonCallableMock(Listener)

    runner = NonCallableMock(ScenarioRunner)
    runner.submit.side_effect = tasks
    scheduler = ScenarioScheduler(runner=runner, listener=listener)
    status = scheduler.run(scenarios)
    assert status is Status.FAILURE

    runner.submit.assert_has_calls([call(scenario) for scenario in scenarios])
    for task in tasks:
        task.result.assert_called_once_with()
    listener.on_scenario.assert_has_calls([call(r) for r in results])
    listener.on_end.assert_called_once_with(Status.FAILURE)


def test_create_scheduler(mocker):
    requester_ctor = mocker.patch(f"{PKG}.Requester", return_value=sentinel.requester)
    unit_runner_ctor = mocker.patch(f"{PKG}.UnitRunner", return_value=sentinel.unit_runner)
    case_runner_ctor = mocker.patch(f"{PKG}.CaseRunner", return_value=sentinel.case_runner)
    runner_ctor = mocker.patch(f"{PKG}.ScenarioRunner", return_value=sentinel.runner)
    scheduler_ctor = mocker.patch(f"{PKG}.ScenarioScheduler", return_value=sentinel.scheduler)

    scheduler = create_scheduler(
        executor=sentinel.executor,
        listener=sentinel.listener,
        base_url=sentinel.base_url,
        timeout=sentinel.timeout,
        retry=sentinel.retry,
        delay=sentinel.delay,
    )
    assert scheduler is sentinel.scheduler

    requester_ctor.assert_called_once_with(base_url=sentinel.base_url, timeout=sentinel.timeout)
    unit_runner_ctor.assert_called_once_with(
        requester=sentinel.requester,
        retry=sentinel.retry,
        delay=sentinel.delay,
    )
    case_runner_ctor.assert_called_once_with(
        unit_runner=sentinel.unit_runner,
        listener=sentinel.listener,
    )
    runner_ctor.assert_called_once_with(
        executor=sentinel.executor,
        case_runner=sentinel.case_runner,
    )
    scheduler_ctor.assert_called_once_with(runner=sentinel.runner, listener=sentinel.listener)
