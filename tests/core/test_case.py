from unittest.mock import ANY, MagicMock, patch, sentinel

from pytest import fixture

from preacher.core.case import Case, CaseListener
from preacher.core.request import Response
from preacher.core.response_description import ResponseVerification
from preacher.core.status import Status
from preacher.core.verification import Verification


@fixture
def response() -> Response:
    return Response(
        id='response-id',
        elapsed=1.23,
        status_code=402,
        headers={},
        body='body',
        request_datetime=sentinel.request_datetime,
    )


@fixture
def retry_patch():
    return patch(
        'preacher.core.case.retry_while_false',
        side_effect=lambda func, *args, **kwargs: func(),
    )


def test_case_listener(response):
    CaseListener().on_response(response)


def test_when_the_request_fails(retry_patch):
    case = Case(
        label='Request fails',
        request=MagicMock(side_effect=RuntimeError('message')),
        response_description=MagicMock(),
    )

    listener = MagicMock(spec=CaseListener)
    with retry_patch as retry:
        result = case('base-url', listener=listener)

    assert not result
    assert result.label == 'Request fails'
    assert result.status == Status.FAILURE
    assert result.request.status == Status.FAILURE
    assert result.request.message == 'RuntimeError: message'

    case.request.assert_called_with('base-url', timeout=None)
    case.response_description.assert_not_called()
    retry.assert_called_once_with(ANY, attempts=1, delay=0.1)

    listener.on_response.assert_not_called()


def test_when_given_an_invalid_response(response, retry_patch):
    case = Case(
        label='Response should be unstable',
        request=MagicMock(return_value=response),
        response_description=MagicMock(verify=MagicMock(
            return_value=ResponseVerification(
                status=Status.UNSTABLE,
                status_code=Verification.succeed(),
                headers=Verification.succeed(),
                body=Verification(status=Status.UNSTABLE)
            ),
        )),
    )

    listener = MagicMock(spec=CaseListener)
    with retry_patch as retry:
        result = case(
            base_url='base-url',
            retry=3,
            delay=1.0,
            timeout=5.0,
            listener=listener,
        )

    assert not result
    assert result.label == 'Response should be unstable'
    assert result.status == Status.UNSTABLE
    assert result.request.status == Status.SUCCESS
    assert result.response.status == Status.UNSTABLE
    assert result.response.body.status == Status.UNSTABLE

    case.request.assert_called_with('base-url', timeout=5.0)
    case.response_description.verify.assert_called_with(
        status_code=402,
        headers={},
        body='body',
        request_datetime=sentinel.request_datetime,
    )
    retry.assert_called_once_with(ANY, attempts=4, delay=1.0)
    listener.on_response.assert_called_once_with(response)


def test_when_given_an_valid_response(response, retry_patch):
    case = Case(
        label='Response should be success',
        request=MagicMock(return_value=response),
        response_description=MagicMock(verify=MagicMock(
            return_value=ResponseVerification(
                status=Status.SUCCESS,
                status_code=Verification.succeed(),
                headers=Verification.succeed(),
                body=Verification.succeed(),
            )
        )),
    )

    with retry_patch:
        result = case(base_url='base-url')

    assert result
    assert result.status == Status.SUCCESS
