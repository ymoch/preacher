from unittest.mock import MagicMock, call, sentinel

from preacher.core.listener import Listener
from preacher.core.runner import ScenarioRunner
from preacher.core.scenario import Scenario, ScenarioResult, ScenarioTask
from preacher.core.scenario.status import Status


def test_given_no_scenario():
    runner = ScenarioRunner()
    status = runner.run(sentinel.executor, [])

    assert status == Status.SKIPPED


def test_given_scenarios():
    results = [
        MagicMock(ScenarioResult, status=Status.UNSTABLE),
        MagicMock(ScenarioResult, status=Status.FAILURE),
    ]
    tasks = [
        MagicMock(ScenarioTask, result=MagicMock(return_value=results[0])),
        MagicMock(ScenarioTask, result=MagicMock(return_value=results[1])),
    ]
    scenarios = [
        MagicMock(Scenario, submit=MagicMock(return_value=tasks[0])),
        MagicMock(Scenario, submit=MagicMock(return_value=tasks[1])),
    ]
    listener = MagicMock(Listener)

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
