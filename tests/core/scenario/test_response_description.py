from typing import List
from unittest.mock import MagicMock, sentinel

from pytest import mark, fixture, raises

from preacher.core.response import Response
from preacher.core.scenario.body_description import BodyDescription
from preacher.core.scenario.analysis_description import AnalysisDescription
from preacher.core.scenario.predicate import Predicate
from preacher.core.scenario.response_description import ResponseDescription
from preacher.core.scenario.status import Status, Statused
from preacher.core.scenario.verification import Verification


@fixture
def response():
    return MagicMock(
        spec=Response,
        id=sentinel.response_id,
        elapsed=sentinel.elapsed,
        status_code=200,
        headers={},
        body=sentinel.body,
        request_datetime=sentinel.starts,
    )


def test_when_given_no_description(response):
    description = ResponseDescription()
    verification = description.verify(response)
    assert verification.response_id == sentinel.response_id
    assert verification.status_code.status == Status.SKIPPED
    assert verification.body.status == Status.SKIPPED
    assert verification.status == Status.SKIPPED


def test_when_header_verification_fails(response):
    headers = [
        MagicMock(AnalysisDescription, verify=MagicMock(
            side_effect=RuntimeError('message')
        )),
    ]
    description = ResponseDescription(headers=headers)

    verification = description.verify(response)
    assert verification.response_id == sentinel.response_id
    assert verification.headers.status == Status.FAILURE


def test_when_given_descriptions(response):
    headers = [
        MagicMock(AnalysisDescription, verify=MagicMock(
            return_value=Verification(status=Status.UNSTABLE)
        )),
        MagicMock(AnalysisDescription, verify=MagicMock(
            return_value=Verification.succeed()
        )),
    ]
    body = MagicMock(
        spec=BodyDescription,
        verify=MagicMock(return_value=Verification(status=Status.UNSTABLE)),
    )
    analyze_headers = MagicMock(return_value=sentinel.headers)
    description = ResponseDescription(
        status_code=[],
        headers=headers,
        body=body,
        analyze_headers=analyze_headers,
    )
    verification = description.verify(response, k='v')
    assert verification.response_id == sentinel.response_id
    assert verification.status == Status.UNSTABLE
    assert verification.status_code.status == Status.SKIPPED
    assert verification.body.status == Status.UNSTABLE

    analyze_headers.assert_called_once_with({})
    for description in headers:
        description.verify.assert_called_once_with(sentinel.headers, k='v')
    body.verify.assert_called_once_with(sentinel.body, k='v')


@mark.parametrize(
    'status_code_status, headers_status, body_status, expected',
    (
        (Status.SUCCESS, Status.SUCCESS, Status.SKIPPED, Status.SUCCESS),
        (Status.UNSTABLE, Status.SKIPPED, Status.SUCCESS, Status.UNSTABLE),
        (Status.SKIPPED, Status.UNSTABLE, Status.SUCCESS, Status.UNSTABLE),
        (Status.SUCCESS, Status.UNSTABLE, Status.FAILURE, Status.FAILURE),
    ),
)
def test_merge_statuses(
    status_code_status: Status,
    headers_status: Status,
    body_status: Status,
    expected: Status,
    response,
):
    status_code_predicates: List[Predicate] = [
        MagicMock(Predicate, verify=MagicMock(
            return_value=Verification(status=status_code_status)
        )),
    ]
    headers_descriptions: List[AnalysisDescription] = [
        MagicMock(AnalysisDescription, verify=MagicMock(
            return_value=Verification(status=headers_status)
        )),
    ]
    body_description: BodyDescription = MagicMock(
        spec=BodyDescription,
        verify=MagicMock(
            return_value=Verification(status=body_status)
        )
    )
    description = ResponseDescription(
        status_code=status_code_predicates,
        headers=headers_descriptions,
        body=body_description,
    )
    verification = description.verify(response)
    assert verification.status == expected


def test_incomplete_statused_implementation():
    class _IncompleteStatused(Statused):

        @property
        def status(self) -> Status:
            return super().status

    statused = _IncompleteStatused()
    with raises(NotImplementedError):
        print(statused.status)
