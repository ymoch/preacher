from unittest.mock import MagicMock, sentinel

from pytest import fixture, raises

from preacher.core.case import Case
from preacher.core.request import Response
from preacher.core.response_description import ResponseVerification
from preacher.core.status import Status
from preacher.core.verification import Verification


@fixture
def response():
    return Response(
        status_code=402,
        headers={},
        body='body',
        request_datetime=sentinel.request_datetime,
    )


def test_when_given_an_invalid_retry_count():
    case = Case(request=MagicMock(), response_description=MagicMock())
    assert case.label is None

    with raises(ValueError):
        case('base-url', retry=-1)


def test_when_the_request_fails():
    case = Case(
        request=MagicMock(side_effect=RuntimeError('message')),
        response_description=MagicMock(),
    )

    verification = case('base-url')
    assert verification.label is None
    assert verification.status == Status.FAILURE
    assert verification.request.status == Status.FAILURE
    assert verification.request.message == 'RuntimeError: message'

    case.request.assert_called_with('base-url')
    case.response_description.assert_not_called()


def test_when_given_an_response(response):
    case = Case(
        label='Response should be unstable',
        request=MagicMock(return_value=response),
        response_description=MagicMock(
            return_value=ResponseVerification(
                status=Status.UNSTABLE,
                status_code=Verification.succeed(),
                body=Verification(status=Status.UNSTABLE)
            ),
        ),
    )
    verification = case(base_url='base-url', retry=1)
    assert verification.label == 'Response should be unstable'
    assert verification.status == Status.UNSTABLE
    assert verification.request.status == Status.SUCCESS
    assert verification.response.status == Status.UNSTABLE
    assert verification.response.body.status == Status.UNSTABLE

    case.response_description.assert_called_with(
        status_code=402,
        body='body',
        request_datetime=sentinel.request_datetime,
    )


def test_when_retrying(response):
    case = Case(
        label='Succeeds',
        request=MagicMock(side_effect=[RuntimeError(), response, response]),
        response_description=MagicMock(
            side_effect=[
                ResponseVerification(
                    status=Status.UNSTABLE,
                    status_code=Verification.succeed(),
                    body=Verification(status=Status.UNSTABLE),
                ),
                ResponseVerification(
                    status=Status.SUCCESS,
                    status_code=Verification.succeed(),
                    body=Verification.succeed(),
                ),
            ]
        ),
    )
    verification = case(base_url='base-url', retry=2)
    assert verification.status == Status.SUCCESS

    assert case.request.call_count == 3
    assert case.response_description.call_count == 2
