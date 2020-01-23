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
    assert result.status == Status.SKIPPED
    assert len(result) == 0

    executor.submit.assert_called_once()


def test_given_cases(executor):
    case_result = MagicMock(CaseResult, status=Status.SUCCESS)
    case = MagicMock(Case, run=MagicMock(return_value=case_result))

    task = OrderedCasesTask(executor, [case], 1, foo='bar')
    result = task.result()
    assert result.status == Status.SUCCESS
    assert result[0] == case_result

    executor.submit.assert_called_once()
    case.run.assert_called_once_with(1, foo='bar')
