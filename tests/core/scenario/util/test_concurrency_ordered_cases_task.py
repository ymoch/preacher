from concurrent.futures import Executor, Future
from unittest.mock import MagicMock

from pytest import fixture

from preacher.core.scenario.status import Status
from preacher.core.scenario.util.concurrency import OrderedCasesTask


def submit(func, *args, **kwargs) -> Future:
    future = Future()
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
