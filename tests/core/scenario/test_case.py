from unittest.mock import ANY, MagicMock, patch, sentinel

from pytest import fixture

from preacher.core.scenario.case import Case, CaseListener
from preacher.core.scenario.request import Request
from preacher.core.scenario.response_description import (
    ResponseDescription,
    ResponseVerification,
)
from preacher.core.scenario.status import Status
from preacher.core.scenario.verification import Verification


PACKAGE = 'preacher.core.scenario.case'


@fixture
def retry_patch():
    return patch(
        'preacher.core.scenario.case.retry_while_false',
        side_effect=lambda func, *args, **kwargs: func(),
    )


def test_case_listener():
    CaseListener().on_response(sentinel.response)


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
        label='Disabled',
        enabled=False,
        request=request,
        response=response
    )
    actual = case.run()
    assert actual.label == 'Disabled'
    assert actual.status is Status.SKIPPED

    request.assert_not_called()
    response.assert_not_called()


def test_when_the_request_fails(retry_patch):
    request = MagicMock(side_effect=RuntimeError('message'))
    response_description = MagicMock(ResponseDescription)
    case = Case(
        label='Request fails',
        request=request,
        response=response_description,
    )

    listener = MagicMock(spec=CaseListener)
    with retry_patch as retry:
        result = case.run(base_url='base-url', listener=listener)

    assert result.label == 'Request fails'
    assert result.status is Status.FAILURE
    assert result.request is request
    assert result.execution.status == Status.FAILURE
    assert result.execution.message == 'RuntimeError: message'

    request.assert_called_once_with('base-url', timeout=None)
    response_description.assert_not_called()
    retry.assert_called_once_with(ANY, attempts=1, delay=0.1)

    listener.on_response.assert_not_called()


def test_when_given_an_invalid_response(retry_patch):
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
        label='Response should be unstable',
        request=request,
        response=response,
    )

    listener = MagicMock(spec=CaseListener)
    with retry_patch as retry:
        result = case.run(
            base_url='base-url',
            retry=3,
            delay=1.0,
            timeout=5.0,
            listener=listener,
        )

    assert result.label == 'Response should be unstable'
    assert result.status == Status.UNSTABLE
    assert result.request is request
    assert result.execution.status == Status.SUCCESS
    assert result.response.status == Status.UNSTABLE
    assert result.response.body.status == Status.UNSTABLE

    request.assert_called_with('base-url', timeout=5.0)
    response.verify.assert_called_with(
        sentinel.response,
        origin_datetime=sentinel.starts,
    )
    retry.assert_called_once_with(ANY, attempts=4, delay=1.0)
    listener.on_response.assert_called_once_with(sentinel.response)


def test_when_given_an_valid_response(retry_patch):
    sentinel.response.starts = sentinel.starts
    case = Case(
        label='Response should be success',
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

    with retry_patch:
        result = case.run()

    assert result.status == Status.SUCCESS
