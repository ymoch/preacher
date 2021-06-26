from typing import List
from unittest.mock import NonCallableMock, Mock, sentinel

from pytest import mark, fixture

from preacher.core.request import Response
from preacher.core.status import Status
from preacher.core.verification.description import Description
from preacher.core.verification.predicate import Predicate
from preacher.core.verification.response import ResponseDescription
from preacher.core.verification.verification import Verification

PKG = "preacher.core.verification.response"


@fixture
def response():
    return NonCallableMock(
        spec=Response,
        id=sentinel.response_id,
        elapsed=sentinel.elapsed,
        status_code=sentinel.status_code,
        headers=sentinel.headers,
        body=sentinel.body,
        request_datetime=sentinel.starts,
    )


def test_when_given_no_description(mocker, response):
    mocker.patch(f"{PKG}.ResponseBodyAnalyzer", return_value=sentinel.body)

    description = ResponseDescription()
    verification = description.verify(response)
    assert verification.response_id == sentinel.response_id
    assert verification.status_code.status == Status.SKIPPED
    assert verification.body.status == Status.SKIPPED
    assert verification.status == Status.SKIPPED


def test_when_given_descriptions(mocker, response):
    analyze_headers = mocker.patch(f"{PKG}.MappingAnalyzer", return_value=sentinel.a_headers)
    analyze_body = mocker.patch(f"{PKG}.ResponseBodyAnalyzer", return_value=sentinel.a_body)

    status_code = [
        NonCallableMock(Predicate, verify=Mock(return_value=Verification(status=Status.UNSTABLE))),
        NonCallableMock(Predicate, verify=Mock(return_value=Verification.succeed())),
    ]
    headers = [
        NonCallableMock(
            Description, verify=Mock(return_value=Verification(status=Status.UNSTABLE))
        ),
        NonCallableMock(Description, verify=Mock(return_value=Verification.succeed())),
    ]
    body = [
        NonCallableMock(
            Description, verify=Mock(return_value=Verification(status=Status.UNSTABLE))
        ),
        NonCallableMock(Description, verify=Mock(return_value=Verification.succeed())),
    ]
    description = ResponseDescription(status_code=status_code, headers=headers, body=body)
    verification = description.verify(response, sentinel.context)
    assert verification.response_id == sentinel.response_id
    assert verification.status == Status.UNSTABLE
    assert verification.status_code.status == Status.UNSTABLE
    assert verification.headers.status == Status.UNSTABLE
    assert verification.body.status == Status.UNSTABLE

    analyze_headers.assert_called_once_with(sentinel.headers)
    analyze_body.assert_called_once_with(sentinel.body)
    for predicate in status_code:
        predicate.verify.assert_called_once_with(sentinel.status_code, sentinel.context)
    for description in headers:
        description.verify.assert_called_once_with(sentinel.a_headers, sentinel.context)
    for description in body:
        description.verify.assert_called_once_with(sentinel.a_body, sentinel.context)


@mark.parametrize(
    ("status_code_status", "headers_status", "body_status", "expected"),
    (
        (Status.SUCCESS, Status.SUCCESS, Status.SKIPPED, Status.SUCCESS),
        (Status.UNSTABLE, Status.SKIPPED, Status.SUCCESS, Status.UNSTABLE),
        (Status.SKIPPED, Status.UNSTABLE, Status.SUCCESS, Status.UNSTABLE),
        (Status.SUCCESS, Status.UNSTABLE, Status.FAILURE, Status.FAILURE),
    ),
)
def test_merge_statuses(
    mocker,
    response,
    status_code_status: Status,
    headers_status: Status,
    body_status: Status,
    expected: Status,
):
    mocker.patch(f"{PKG}.MappingAnalyzer", return_value=sentinel.a_headers)
    mocker.patch(f"{PKG}.ResponseBodyAnalyzer", return_value=sentinel.a_body)

    status_code: List[Predicate] = [
        NonCallableMock(
            Predicate, verify=Mock(return_value=Verification(status=status_code_status))
        ),
    ]
    headers: List[Description] = [
        NonCallableMock(
            Description, verify=Mock(return_value=Verification(status=headers_status))
        ),
    ]
    body_description: List[Description] = [
        NonCallableMock(Description, verify=Mock(return_value=Verification(status=body_status))),
    ]
    description = ResponseDescription(
        status_code=status_code,
        headers=headers,
        body=body_description,
    )
    verification = description.verify(response)
    assert verification.status is expected
