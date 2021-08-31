from concurrent.futures import Executor, Future
from unittest.mock import MagicMock, NonCallableMock, call, sentinel

from pytest import fixture
from requests import Session

from preacher.core.scenario.case_result import CaseResult
from preacher.core.scenario.case_runner import CaseRunner
from preacher.core.scenario.util.concurrency import OrderedCasesTask
from preacher.core.status import Status

PACKAGE = "preacher.core.scenario.util.concurrency"


def submit(func, *args, **kwargs) -> Future:
    future: Future = Future()
    future.set_result(func(*args, **kwargs))
    return future


@fixture
def executor():
    executor = NonCallableMock(Executor)
    executor.submit.side_effect = submit
    return executor


def test_given_no_cases(executor):
    runner = NonCallableMock(CaseRunner)
    task = OrderedCasesTask(executor, runner, [])
    result = task.result()
    assert result.status is Status.SKIPPED
    assert not result.items

    executor.submit.assert_called_once()
    runner.run.assert_not_called()


def test_given_cases(mocker, executor):
    session = MagicMock(Session)
    session.__enter__.return_value = session
    session_ctor = mocker.patch(f"{PACKAGE}.Session", return_value=session)

    case_results = [
        NonCallableMock(CaseResult, status=Status.SUCCESS),
        NonCallableMock(CaseResult, status=Status.UNSTABLE),
    ]
    runner = NonCallableMock(CaseRunner)
    runner.run.side_effect = case_results
    cases = [sentinel.case1, sentinel.case2]

    task = OrderedCasesTask(executor, runner, cases, context=sentinel.context)
    result = task.result()
    assert result.status is Status.UNSTABLE
    assert result.items == case_results

    executor.submit.assert_called_once()
    runner.run.assert_has_calls(
        [
            call(sentinel.case1, session=session, context=sentinel.context),
            call(sentinel.case2, session=session, context=sentinel.context),
        ]
    )

    session_ctor.assert_called_once()
    session.__exit__.assert_called()
