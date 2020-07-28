from unittest.mock import ANY, Mock, NonCallableMock, sentinel

from pytest import mark

from preacher.core.request.request import Request, ExecutionReport
from preacher.core.scenario.case import Case, CaseListener
from preacher.core.status import Status
from preacher.core.value import ValueContext
from preacher.core.verification import Description
from preacher.core.verification import ResponseDescription
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


def test_when_disabled():
    request = NonCallableMock(Request)
    response = NonCallableMock(ResponseDescription)
    case = Case(
        label=sentinel.label,
        enabled=False,
        request=request,
        response=response
    )
    actual = case.run()
    assert actual.label is sentinel.label
    assert actual.status is Status.SKIPPED

    request.execute.assert_not_called()
    response.verify.assert_not_called()


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
    request = NonCallableMock(Request)
    response = NonCallableMock(ResponseDescription)
    case = Case(
        label=sentinel.label,
        conditions=conditions,
        request=request,
        response=response,
    )

    listener = NonCallableMock(CaseListener)
    result = case.run(listener=listener)

    assert result.label is sentinel.label
    assert result.status is expected_status

    request.execute.assert_not_called()
    response.verify.assert_not_called()
    listener.on_execution.assert_not_called()


def test_when_given_no_response(mocker):
    retry = mocker.patch(f'{PKG}.retry_while_false', side_effect=_retry)

    execution = ExecutionReport(status=Status.FAILURE)
    request = NonCallableMock(Request)
    request.execute.return_value = (execution, None)
    response = NonCallableMock(ResponseDescription)
    case = Case(label=sentinel.label, request=request, response=response)

    listener = NonCallableMock(spec=CaseListener)
    result = case.run(base_url=sentinel.base_url, listener=listener)

    assert result.label is sentinel.label
    assert result.status is Status.FAILURE
    assert result.execution is execution
    assert result.response is None

    request.execute.assert_called_once_with(sentinel.base_url, timeout=None, session=None)
    response.verify.assert_not_called()
    retry.assert_called_once_with(ANY, attempts=1, delay=0.1)

    listener.on_execution.assert_called_once_with(execution, None)


def test_when_given_an_response(mocker):
    retry = mocker.patch(f'{PKG}.retry_while_false', side_effect=_retry)

    execution = ExecutionReport(status=Status.SUCCESS, starts=sentinel.starts)
    request = NonCallableMock(Request)
    request.execute.return_value = (execution, sentinel.response)

    response_verification = ResponseVerification(
        response_id=sentinel.response_id,
        status_code=Verification.succeed(),
        headers=Verification.succeed(),
        body=Verification(status=Status.UNSTABLE)
    )
    response = NonCallableMock(ResponseDescription)
    response.verify.return_value = response_verification

    case = Case(label=sentinel.label, request=request, response=response)

    listener = NonCallableMock(spec=CaseListener)
    result = case.run(
        base_url=sentinel.base_url,
        retry=3,
        delay=sentinel.delay,
        timeout=sentinel.timeout,
        listener=listener,
        session=sentinel.session,
    )

    assert result.label is sentinel.label
    assert result.status is Status.UNSTABLE
    assert result.execution is execution
    assert result.response is response_verification

    request.execute.assert_called_with(
        sentinel.base_url,
        timeout=sentinel.timeout,
        session=sentinel.session,
    )
    response.verify.assert_called_with(
        sentinel.response,
        ValueContext(origin_datetime=sentinel.starts),
    )
    retry.assert_called_once_with(ANY, attempts=4, delay=sentinel.delay)
    listener.on_execution.assert_called_once_with(execution, sentinel.response)
