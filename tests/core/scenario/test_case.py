from unittest.mock import ANY, MagicMock, patch, sentinel

from pytest import mark

from preacher.core.scenario import AnalysisDescription
from preacher.core.scenario.case import Case, CaseListener
from preacher.core.scenario.request import Request
from preacher.core.scenario.response_description import (
    ResponseDescription,
    ResponseVerification,
)
from preacher.core.scenario.status import Status
from preacher.core.scenario.verification import Verification

PACKAGE = 'preacher.core.scenario.case'

retry_patch = patch(
    f'{PACKAGE}.retry_while_false',
    side_effect=lambda func, *args, **kwargs: func(),
)


def test_case_listener():
    CaseListener().on_response(sentinel.response)


@mark.parametrize(
    'condition_verifications, expected_status', [
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
    ]
)
def test_given_bad_condition(condition_verifications, expected_status):
    conditions = [
        MagicMock(AnalysisDescription, verify=MagicMock(return_value=v))
        for v in condition_verifications
    ]
    request = MagicMock(Request)
    case = Case(label=sentinel.label, conditions=conditions, request=request)
    result = case.run()

    assert result.label is sentinel.label
    assert result.status is expected_status

    request.assert_not_called()


@patch(f'{PACKAGE}.Request', return_value=sentinel.request)
@patch(f'{PACKAGE}.ResponseDescription', return_value=sentinel.response)
def test_default_construction(response_ctor, request_ctor):
    case = Case()
    assert case.label is None
    assert case.enabled
    assert case.request is sentinel.request
    assert case.response is sentinel.response

    request_ctor.assert_called_once_with()
    response_ctor.assert_called_once_with()


def test_when_disabled():
    request = MagicMock(Request)
    response = MagicMock(ResponseDescription)
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


@retry_patch
def test_when_the_request_fails(retry):
    request = MagicMock(side_effect=RuntimeError('message'))
    response_description = MagicMock(ResponseDescription)
    case = Case(
        label=sentinel.label,
        request=request,
        response=response_description,
    )

    listener = MagicMock(spec=CaseListener)
    result = case.run(base_url=sentinel.base_url, listener=listener)

    assert result.label is sentinel.label
    assert result.status is Status.FAILURE
    assert result.request is request
    assert result.execution.status is Status.FAILURE
    assert result.execution.message == 'RuntimeError: message'

    request.assert_called_once_with(sentinel.base_url, timeout=None)
    response_description.assert_not_called()
    retry.assert_called_once_with(ANY, attempts=1, delay=0.1)

    listener.on_response.assert_not_called()


@retry_patch
def test_when_given_an_invalid_response(retry):
    sentinel.response.starts = sentinel.starts
    request = MagicMock(return_value=sentinel.response)
    response = MagicMock(ResponseDescription, verify=MagicMock(
        return_value=ResponseVerification(
            response_id=sentinel.response_id,
            status=Status.UNSTABLE,
            status_code=Verification.succeed(),
            headers=Verification.succeed(),
            body=Verification(status=Status.UNSTABLE)
        ),
    ))
    case = Case(
        label=sentinel.label,
        request=request,
        response=response,
    )

    listener = MagicMock(spec=CaseListener)
    result = case.run(
        base_url=sentinel.base_url,
        retry=3,
        delay=sentinel.delay,
        timeout=sentinel.timeout,
        listener=listener,
    )

    assert result.label is sentinel.label
    assert result.status is Status.UNSTABLE
    assert result.request is request
    assert result.execution.status is Status.SUCCESS
    assert result.response.status is Status.UNSTABLE
    assert result.response.body.status is Status.UNSTABLE

    request.assert_called_with(sentinel.base_url, timeout=sentinel.timeout)
    response.verify.assert_called_with(
        sentinel.response,
        origin_datetime=sentinel.starts,
    )
    retry.assert_called_once_with(ANY, attempts=4, delay=sentinel.delay)
    listener.on_response.assert_called_once_with(sentinel.response)


@retry_patch
def test_when_given_an_valid_response(retry):
    sentinel.response.starts = sentinel.starts
    case = Case(
        label=sentinel.label,
        conditions=[
            MagicMock(
                spec=AnalysisDescription,
                verify=MagicMock(return_value=Verification.succeed()),
            ),
        ],
        request=MagicMock(return_value=sentinel.response),
        response=MagicMock(verify=MagicMock(
            return_value=ResponseVerification(
                response_id=sentinel.response_id,
                status=Status.SUCCESS,
                status_code=Verification.succeed(),
                headers=Verification.succeed(),
                body=Verification.succeed(),
            )
        )),
    )
    result = case.run()

    assert result.label is sentinel.label
    assert result.status is Status.SUCCESS
    assert result.conditions.status is Status.SUCCESS
    assert result.execution.status is Status.SUCCESS
    assert result.response.status is Status.SUCCESS
