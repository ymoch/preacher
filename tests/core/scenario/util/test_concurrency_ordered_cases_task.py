from concurrent.futures import Executor, Future
from unittest.mock import MagicMock, NonCallableMock, call, sentinel

from pytest import fixture
from requests import Session

from preacher.core.scenario.case_result import CaseResult
from preacher.core.scenario.case_runner import CaseRunner
from preacher.core.scenario.util.concurrency import OrderedCasesTask
from preacher.core.status import Status

PACKAGE = 'preacher.core.scenario.util.concurrency'


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
    task = OrderedCasesTask(executor, case_runner, [])
    result = task.result()
    assert result.status is Status.SKIPPED
    assert not result.items

    executor.submit.assert_called_once()
    case_runner.run.assert_not_called()


def test_given_cases(mocker, executor):
    session = MagicMock(Session)
    session.__enter__.return_value = session
    session_ctor = mocker.patch(f'{PACKAGE}.Session', return_value=session)

    case_results = [
        NonCallableMock(CaseResult, status=Status.SUCCESS),
        NonCallableMock(CaseResult, status=Status.UNSTABLE),
    ]
    case_runner = NonCallableMock(CaseRunner)
    case_runner.run.side_effect = case_results
    cases = [sentinel.case1, sentinel.case2]

    task = OrderedCasesTask(executor, case_runner, cases, 1, foo='bar')
    result = task.result()
    assert result.status is Status.UNSTABLE
    assert result.items == case_results

    executor.submit.assert_called_once()
    case_runner.run.assert_has_calls([
        call(sentinel.case1, 1, foo='bar', session=session),
        call(sentinel.case2, 1, foo='bar', session=session),
    ])

    session_ctor.assert_called_once()
    session.__exit__.assert_called()


def test_given_cases_with_session(mocker, executor):
    session_ctor = mocker.patch(f'{PACKAGE}.Session')

    case_results = [MagicMock(CaseResult, status=Status.SUCCESS)]
    case_runner = NonCallableMock(CaseRunner)
    case_runner.run.side_effect = case_results
    cases = [sentinel.case]

    task = OrderedCasesTask(executor, case_runner, cases, 2, session=sentinel.session)
    task.result()

    case_runner.run.assert_called_with(sentinel.case, 2, session=sentinel.session)
    session_ctor.assert_not_called()
