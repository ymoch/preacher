from unittest.mock import ANY, NonCallableMock, sentinel

from pytest import mark, raises

from preacher.core.request import ExecutionReport, Requester
from preacher.core.status import Status
from preacher.core.unit.runner import predicate, UnitRunner
from preacher.core.verification import ResponseVerification, ResponseDescription

PKG = "preacher.core.unit.runner"


def _retry(func, *_args, **_kwargs):
    return func()


@mark.parametrize(
    ("execution", "verification", "expected"),
    (
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
    ),
)
def test_predicate(execution, verification, expected):
    assert predicate((execution, None, verification)) == expected


@mark.parametrize("retry", [-2, -1])
def test_given_invalid_retry_count(retry):
    with raises(ValueError):
        UnitRunner(sentinel.requester, retry=retry)


def test_given_no_response(mocker):
    retry = mocker.patch(f"{PKG}.retry_while_false", side_effect=_retry)

    requester = NonCallableMock(Requester)
    requester.base_url = sentinel.requester_base_url
    requester.execute.return_value = (sentinel.execution, None)

    requirements = NonCallableMock(ResponseDescription)

    runner = UnitRunner(requester)
    assert runner.base_url is sentinel.requester_base_url

    execution, response, verification = runner.run(sentinel.request, requirements)
    assert execution is sentinel.execution
    assert response is None
    assert verification is None

    requester.execute.assert_called_once_with(sentinel.request, session=None)
    requirements.verify.assert_not_called()
    retry.assert_called_once_with(ANY, attempts=1, delay=0.1, predicate=predicate)


def test_given_a_response(mocker):
    retry = mocker.patch(f"{PKG}.retry_while_false", side_effect=_retry)

    execution = ExecutionReport(starts=sentinel.starts)
    requester = NonCallableMock(Requester)
    requester.base_url = sentinel.requester_base_url
    requester.execute.return_value = (execution, sentinel.response)

    requirements = NonCallableMock(ResponseDescription)
    requirements.verify.return_value = sentinel.verification

    runner = UnitRunner(requester=requester, retry=3, delay=sentinel.delay)
    assert runner.base_url is sentinel.requester_base_url

    execution, response, verification = runner.run(
        sentinel.request,
        requirements,
        sentinel.session,
    )
    assert execution is execution
    assert response is sentinel.response
    assert verification is sentinel.verification

    requester.execute.assert_called_with(sentinel.request, session=sentinel.session)
    requirements.verify.assert_called_with(
        sentinel.response,
        {"starts": sentinel.starts, "base_url": sentinel.requester_base_url},
    )
    retry.assert_called_once_with(ANY, attempts=4, delay=sentinel.delay, predicate=ANY)
