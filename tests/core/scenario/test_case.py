from unittest.mock import Mock, NonCallableMock, sentinel

from pytest import mark

from preacher.core.request import ExecutionReport
from preacher.core.scenario import CaseListener
from preacher.core.scenario.case import Case
from preacher.core.scenario.case_runner import CaseRunner
from preacher.core.status import Status
from preacher.core.unit import UnitRunner
from preacher.core.verification import Description
from preacher.core.verification import ResponseVerification
from preacher.core.verification import Verification

PKG = 'preacher.core.scenario.case'


def _retry(func, *_args, **_kwargs):
    return func()


def test_case_listener():
    CaseListener().on_execution(sentinel.execution, sentinel.response)


def test_default_construction(mocker):
    request_ctor = mocker.patch(f'{PKG}.Request')
    request_ctor.return_value = sentinel.request
    response_ctor = mocker.patch(f'{PKG}.ResponseDescription')
    response_ctor.return_value = sentinel.response

    case = Case()
    assert case.label is None
    assert case.enabled
    assert case.request is sentinel.request
    assert case.response is sentinel.response

    request_ctor.assert_called_once_with()
    response_ctor.assert_called_once_with()


def test_runner_properties():
    unit_runner = NonCallableMock(UnitRunner, base_url=sentinel.base_url)
    runner = CaseRunner(unit_runner)
    assert runner.base_url is sentinel.base_url


def test_when_disabled():
    case = Case(
        label=sentinel.label,
        enabled=False,
        request=sentinel.request,
        response=sentinel.response,
    )

    unit_runner = NonCallableMock(UnitRunner)
    runner = CaseRunner(unit_runner)
    actual = runner.run(case)
    assert actual.label is sentinel.label
    assert actual.status is Status.SKIPPED

    unit_runner.run.assert_not_called()


@mark.parametrize(('condition_verifications', 'expected_status'), [
    (
        [
            Verification(status=Status.SKIPPED),
            Verification(status=Status.UNSTABLE),
            Verification(status=Status.SUCCESS),
        ],
        Status.SKIPPED,
    ),
    (
        [
            Verification(status=Status.SUCCESS),
            Verification(status=Status.FAILURE),
            Verification(status=Status.UNSTABLE),
        ],
        Status.FAILURE,
    ),
])
def test_given_bad_condition(condition_verifications, expected_status):
    conditions = [
        NonCallableMock(Description, verify=Mock(return_value=v))
        for v in condition_verifications
    ]
    case = Case(
        label=sentinel.label,
        conditions=conditions,
        request=sentinel.request,
        response=sentinel.response,
    )

    unit_runner = NonCallableMock(UnitRunner)
    runner = CaseRunner(unit_runner)
    listener = NonCallableMock(CaseListener)
    result = runner.run(case, listener=listener)

    assert result.label is sentinel.label
    assert result.status is expected_status

    unit_runner.run.assert_not_called()
    listener.on_execution.assert_not_called()


def test_when_given_no_response():
    execution = ExecutionReport(status=Status.FAILURE)
    case = Case(label=sentinel.label, request=sentinel.request, response=sentinel.response)

    unit_runner = NonCallableMock(UnitRunner)
    unit_runner.run.return_value = (execution, None, None)
    runner = CaseRunner(unit_runner)
    listener = NonCallableMock(spec=CaseListener)
    result = runner.run(case, listener)

    assert result.label is sentinel.label
    assert result.status is Status.FAILURE
    assert result.execution is execution
    assert result.response is None

    unit_runner.run.assert_called_once_with(
        request=sentinel.request,
        requirements=sentinel.response,
        session=None,
    )
    listener.on_execution.assert_called_once_with(execution, None)


def test_when_given_an_response():
    execution = ExecutionReport(status=Status.SUCCESS, starts=sentinel.starts)
    verification = ResponseVerification(
        response_id=sentinel.response_id,
        status_code=Verification.succeed(),
        headers=Verification.succeed(),
        body=Verification(status=Status.UNSTABLE)
    )

    case = Case(label=sentinel.label, request=sentinel.request, response=sentinel.response)

    unit_runner = NonCallableMock(UnitRunner)
    unit_runner.run.return_value = (execution, sentinel.response, verification)
    runner = CaseRunner(unit_runner)
    listener = NonCallableMock(spec=CaseListener)
    result = runner.run(case, listener, sentinel.session)

    assert result.label is sentinel.label
    assert result.status is Status.UNSTABLE
    assert result.execution is execution
    assert result.response is verification

    unit_runner.run.assert_called_once_with(
        request=sentinel.request,
        requirements=sentinel.response,
        session=sentinel.session,
    )
    listener.on_execution.assert_called_once_with(execution, sentinel.response)
