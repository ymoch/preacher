from concurrent.futures import Executor, Future
from unittest.mock import MagicMock

from pytest import fixture

from preacher.core.scenario.case import CaseResult, Case
from preacher.core.scenario.status import Status
from preacher.core.scenario.util.concurrency import UnorderedCasesTask


def submit(func, *args, **kwargs) -> Future:
    future: Future = Future()
    future.set_result(func(*args, **kwargs))
    return future


@fixture
def executor():
    executor = MagicMock(Executor)
    executor.submit = MagicMock(side_effect=submit)
    return executor


def test_given_no_cases(executor):
    task = UnorderedCasesTask(executor, [])
    result = task.result()
    assert result.status is Status.SKIPPED
    assert not result.items

    executor.submit.assert_not_called()


def test_given_cases(executor):
    case_results = [
        MagicMock(CaseResult, status=Status.UNSTABLE),
        MagicMock(CaseResult, status=Status.FAILURE),
    ]
    cases = [
        MagicMock(Case, run=MagicMock(return_value=result))
        for result in case_results
    ]

    task = UnorderedCasesTask(executor, cases, 1, foo='bar')
    result = task.result()
    assert result.status is Status.FAILURE
    assert result.items == case_results

    assert executor.submit.call_count == len(cases)
    for case in cases:
        case.run.assert_called_once_with(1, foo='bar')
