from concurrent.futures import Executor, Future
from unittest.mock import NonCallableMock, call, sentinel

from pytest import fixture

from preacher.core.scenario.case_result import CaseResult
from preacher.core.scenario.case_runner import CaseRunner
from preacher.core.scenario.util.concurrency import UnorderedCasesTask
from preacher.core.status import Status


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
    case_runner = NonCallableMock(CaseRunner)
    task = UnorderedCasesTask(executor, case_runner, [])
    result = task.result()
    assert result.status is Status.SKIPPED
    assert not result.items

    executor.submit.assert_not_called()
    case_runner.run.assert_not_called()


def test_given_cases(executor):
    case_results = [
        NonCallableMock(CaseResult, status=Status.UNSTABLE),
        NonCallableMock(CaseResult, status=Status.FAILURE),
    ]
    case_runner = NonCallableMock(CaseRunner)
    case_runner.run.side_effect = case_results
    cases = [sentinel.case1, sentinel.case2]

    task = UnorderedCasesTask(executor, case_runner, cases, 1, foo='bar')
    result = task.result()
    assert result.status is Status.FAILURE
    assert result.items == case_results

    assert executor.submit.call_count == 2
    case_runner.run.assert_has_calls([
        call(sentinel.case1, 1, foo='bar'),
        call(sentinel.case2, 1, foo='bar'),
    ])
