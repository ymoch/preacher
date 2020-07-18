from concurrent.futures import Executor, Future
from unittest.mock import MagicMock, patch, sentinel

from pytest import fixture
from requests import Session

from preacher.core.scenario.case import Case, CaseResult
from preacher.core.scenario.util.concurrency import OrderedCasesTask
from preacher.core.status import Status

PACKAGE = 'preacher.core.scenario.util.concurrency'


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

    session = MagicMock(Session)
    session.__enter__.return_value = session
    with patch(f'{PACKAGE}.Session', return_value=session):
        task = OrderedCasesTask(executor, cases, 1, foo='bar')
        result = task.result()
    assert result.status is Status.UNSTABLE
    assert result.items == case_results

    executor.submit.assert_called_once()
    for case in cases:
        case.run.assert_called_once_with(1, foo='bar', session=session)

    session.__exit__.assert_called()


def test_given_cases_with_session(executor):
    case_results = [
        MagicMock(CaseResult, status=Status.SUCCESS),
    ]
    cases = [
        MagicMock(Case, run=MagicMock(return_value=result))
        for result in case_results
    ]
    with patch(f'{PACKAGE}.Session') as session_ctor:
        task = OrderedCasesTask(
            executor,
            cases,
            2,
            spam='ham',
            session=sentinel.session,
        )
        task.result()

    for case in cases:
        case.run.assert_called_once_with(
            2,
            spam='ham',
            session=sentinel.session,
        )

    session_ctor.assert_not_called()
