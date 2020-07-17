from unittest.mock import ANY, Mock, NonCallableMock, sentinel

from pytest import mark

from preacher.core.request.request import Request
from preacher.core.scenario.case import Case, CaseListener
from preacher.core.scenario.description import Description
from preacher.core.scenario.response import (
    ResponseDescription,
    ResponseVerification,
)
from preacher.core.scenario.status import Status
from preacher.core.scenario.verification import Verification
from preacher.core.value import ValueContext

PKG = 'preacher.core.scenario.case'


def _retry(func, *_args, **_kwargs):
    return func()


def test_case_listener():
    CaseListener().on_response(sentinel.response)


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
    request = Mock(Request)
    response = NonCallableMock(ResponseDescription)
    case = Case(
        label=sentinel.label,
        conditions=conditions,
        request=request,
        response=response,
    )
    result = case.run()

    assert result.label is sentinel.label
    assert result.status is expected_status

    request.assert_not_called()
    response.verify.assert_not_called()


def test_when_disabled():
    request = Mock(Request)
    response = Mock(ResponseDescription)
    case = Case(
        label=sentinel.label,
        enabled=False,
        request=request,
        response=response
    )
    actual = case.run()
    assert actual.label is sentinel.label
    assert actual.status is Status.SKIPPED

    request.assert_not_called()
    response.verify.assert_not_called()


def test_when_the_request_fails(mocker):
    retry = mocker.patch(f'{PKG}.retry_while_false', side_effect=_retry)

    request = Mock(side_effect=RuntimeError('message'))
    response = NonCallableMock(ResponseDescription)
    case = Case(label=sentinel.label, request=request, response=response)

    listener = NonCallableMock(spec=CaseListener)
    result = case.run(base_url=sentinel.base_url, listener=listener)

    assert result.label is sentinel.label
    assert result.status is Status.FAILURE
    assert result.request is request
    assert result.execution.status is Status.FAILURE
    assert result.execution.message == 'RuntimeError: message'
    assert result.response is None

    request.assert_called_once_with(
        sentinel.base_url,
        timeout=None,
        session=None,
    )
    response.verify.assert_not_called()
    retry.assert_called_once_with(ANY, attempts=1, delay=0.1)

    listener.on_response.assert_not_called()


def test_when_given_an_response(mocker):
    retry = mocker.patch(f'{PKG}.retry_while_false', side_effect=_retry)

    sentinel.response.starts = sentinel.starts
    request = Mock(return_value=sentinel.response)
    response = NonCallableMock(ResponseDescription, verify=Mock(
        return_value=ResponseVerification(
            response_id=sentinel.response_id,
            status=Status.UNSTABLE,
            status_code=Verification.succeed(),
            headers=Verification.succeed(),
            body=Verification(status=Status.UNSTABLE)
        ),
    ))
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
    assert result.request is request
    assert result.execution.status is Status.SUCCESS
    assert result.response.status is Status.UNSTABLE
    assert result.response.body.status is Status.UNSTABLE

    request.assert_called_with(
        sentinel.base_url,
        timeout=sentinel.timeout,
        session=sentinel.session,
    )
    response.verify.assert_called_with(
        sentinel.response,
        ValueContext(origin_datetime=sentinel.starts),
    )
    retry.assert_called_once_with(ANY, attempts=4, delay=sentinel.delay)
    listener.on_response.assert_called_once_with(sentinel.response)
