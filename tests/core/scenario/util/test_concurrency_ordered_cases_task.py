from concurrent.futures import Executor, Future
from unittest.mock import MagicMock

from pytest import fixture

from preacher.core.scenario.case import Case, CaseResult
from preacher.core.scenario.status import Status
from preacher.core.scenario.util.concurrency import OrderedCasesTask


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
    task = OrderedCasesTask(executor, [])
    result = task.result()
    assert result.status is Status.SKIPPED
    assert not result.items

    executor.submit.assert_called_once()


def test_given_cases(executor):
    case_results = [
        MagicMock(CaseResult, status=Status.SUCCESS),
        MagicMock(CaseResult, status=Status.UNSTABLE),
    ]
    cases = [
        MagicMock(Case, run=MagicMock(return_value=result))
        for result in case_results
    ]

    task = OrderedCasesTask(executor, cases, 1, foo='bar')
    result = task.result()
    assert result.status is Status.UNSTABLE
    assert result.items == case_results

    executor.submit.assert_called_once()
    for case in cases:
        case.run.assert_called_once_with(1, foo='bar')
