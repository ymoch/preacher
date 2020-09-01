from unittest.mock import ANY, NonCallableMock, sentinel

from pytest import mark, raises

from preacher.core.request import ExecutionReport, Request
from preacher.core.status import Status
from preacher.core.unit.runner import predicate, UnitRunner
from preacher.core.value import ValueContext
from preacher.core.verification import ResponseVerification, ResponseDescription

PKG = 'preacher.core.unit.runner'


def _retry(func, *_args, **_kwargs):
    return func()


@mark.parametrize(('execution', 'verification', 'expected'), [
    (ExecutionReport(Status.UNSTABLE), None, False),
    (ExecutionReport(Status.SUCCESS), None, True),
    (
        ExecutionReport(Status.UNSTABLE),
        NonCallableMock(ResponseVerification, status=Status.SUCCESS),
        False,
    ),
    (
        ExecutionReport(Status.SUCCESS),
        NonCallableMock(ResponseVerification, status=Status.FAILURE),
        False,
    ),
    (
        ExecutionReport(Status.SUCCESS),
        NonCallableMock(ResponseVerification, status=Status.SUCCESS),
        True,
    ),
])
def test_predicate(execution, verification, expected):
    assert predicate((execution, None, verification)) == expected


@mark.parametrize('retry', [-2, -1])
def test_given_invalid_retry_count(retry):
    with raises(ValueError):
        UnitRunner(sentinel.base_url, retry=retry)


def test_given_no_response(mocker):
    retry = mocker.patch(f'{PKG}.retry_while_false', side_effect=_retry)

    request = NonCallableMock(Request)
    request.execute.return_value = (sentinel.execution, None)
    requirements = NonCallableMock(ResponseDescription)

    runner = UnitRunner(sentinel.base_url)
    execution, response, verification = runner.run(request, requirements)

    assert execution is sentinel.execution
    assert response is None
    assert verification is None

    request.execute.assert_called_once_with(sentinel.base_url, timeout=None, session=None)
    requirements.verify.assert_not_called()
    retry.assert_called_once_with(ANY, attempts=1, delay=0.1, predicate=predicate)


def test_given_a_response(mocker):
    retry = mocker.patch(f'{PKG}.retry_while_false', side_effect=_retry)

    execution = ExecutionReport(starts=sentinel.starts)
    request = NonCallableMock(Request)
    request.execute.return_value = (execution, sentinel.response)
    requirements = NonCallableMock(ResponseDescription)
    requirements.verify.return_value = sentinel.verification

    runner = UnitRunner(
        base_url=sentinel.base_url,
        retry=3,
        delay=sentinel.delay,
        timeout=sentinel.timeout,
    )
    execution, response, verification = runner.run(request, requirements, sentinel.session)

    assert execution is execution
    assert response is sentinel.response
    assert verification is sentinel.verification

    request.execute.assert_called_with(
        sentinel.base_url,
        timeout=sentinel.timeout,
        session=sentinel.session,
    )
    requirements.verify.assert_called_with(
        sentinel.response,
        ValueContext(origin_datetime=sentinel.starts),
    )
    retry.assert_called_once_with(ANY, attempts=4, delay=sentinel.delay, predicate=ANY)
