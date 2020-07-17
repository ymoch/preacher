from typing import Iterable, Iterator
from unittest.mock import Mock, NonCallableMock, call, sentinel

from preacher.core.listener import Listener
from preacher.core.runner import ScenarioRunner
from preacher.core.scenario import Scenario, ScenarioResult, ScenarioTask
from preacher.core.status import Status


def test_given_no_scenario():
    runner = ScenarioRunner()
    status = runner.run(sentinel.executor, [])

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
                raise Exception('message')
            if self._count > 3:
                raise StopIteration()

            successful_result = ScenarioResult(status=Status.SUCCESS)
            successful_task = NonCallableMock(ScenarioTask)
            successful_task.result.return_value = successful_result
            successful = NonCallableMock(Scenario)
            successful.submit.return_value = successful_task
            return successful

    runner = ScenarioRunner()
    listener = NonCallableMock(Listener)
    status = runner.run(sentinel.executor, _Scenarios(), listener)
    assert status is Status.FAILURE

    print(listener.on_scenario.call_args_list)

    results = [c[0][0] for c in listener.on_scenario.call_args_list]
    assert len(results) == 3

    first_successful = results[0]
    assert first_successful.status is Status.SUCCESS

    construction_failure = results[1]
    assert construction_failure.label == 'Not a constructed scenario'
    assert construction_failure.status is Status.FAILURE
    assert construction_failure.message == 'Exception: message'

    second_successful = results[2]
    assert second_successful.status is Status.SUCCESS


def test_given_scenarios():
    results = [
        ScenarioResult(status=Status.UNSTABLE),
        ScenarioResult(status=Status.FAILURE),
    ]
    tasks = [
        NonCallableMock(ScenarioTask, result=Mock(return_value=results[0])),
        NonCallableMock(ScenarioTask, result=Mock(return_value=results[1])),
    ]
    scenarios = [
        NonCallableMock(Scenario, submit=Mock(return_value=tasks[0])),
        NonCallableMock(Scenario, submit=Mock(return_value=tasks[1])),
    ]
    listener = NonCallableMock(Listener)

    runner = ScenarioRunner(
        base_url=sentinel.base_url,
        retry=sentinel.retry,
        delay=sentinel.delay,
        timeout=sentinel.timeout,
    )
    status = runner.run(sentinel.executor, scenarios, listener=listener)

    assert status == Status.FAILURE
    for scenario in scenarios:
        scenario.submit.assert_called_once_with(
            sentinel.executor,
            base_url=sentinel.base_url,
            retry=sentinel.retry,
            delay=sentinel.delay,
            timeout=sentinel.timeout,
            listener=listener,
        )
    for task in tasks:
        task.result.assert_called_once_with()
    listener.on_scenario.assert_has_calls([call(r) for r in results])
    listener.on_end.assert_called_once_with(Status.FAILURE)
