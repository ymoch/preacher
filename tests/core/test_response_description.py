from unittest.mock import MagicMock, sentinel

from pytest import mark

from preacher.core.body_description import BodyDescription
from preacher.core.description import Description
from preacher.core.predicate import Predicate
from preacher.core.request import Response
from preacher.core.response import ResponseDescription
from preacher.core.status import Status
from preacher.core.verification import Verification


def test_when_given_no_description():
    description = ResponseDescription()
    verification = description.verify(
        Response(
            id=sentinel.response_id,
            elapsed=sentinel.elapsed,
            status_code=200,
            headers={},
            body='xxx',
            request_datetime=sentinel.request_datetime
        ),
    )
    assert verification.response_id == sentinel.response_id
    assert verification.status_code.status == Status.SKIPPED
    assert verification.body.status == Status.SKIPPED
    assert verification.status == Status.SKIPPED


def test_when_header_verification_fails():
    headers_descriptions = [
        MagicMock(Description, verify=MagicMock(
            side_effect=RuntimeError('message')
        )),
    ]
    description = ResponseDescription(
        headers_descriptions=headers_descriptions
    )

    verification = description.verify(
        Response(
            id=sentinel.response_id,
            elapsed=sentinel.elapsed,
            status_code=200,
            headers={},
            body='xxx',
            request_datetime=sentinel.request_datetime
        ),
    )
    assert verification.response_id == sentinel.response_id
    assert verification.headers.status == Status.FAILURE


def test_when_given_descriptions():
    headers_descriptions = [
        MagicMock(Description, verify=MagicMock(
            return_value=Verification(status=Status.UNSTABLE)
        )),
        MagicMock(Description, verify=MagicMock(
            return_value=Verification.succeed()
        )),
    ]
    body_description = MagicMock(
        spec=BodyDescription,
        verify=MagicMock(return_value=Verification(status=Status.UNSTABLE)),
    )
    analyze_headers = MagicMock(return_value=sentinel.headers)
    description = ResponseDescription(
        status_code_predicates=[],
        headers_descriptions=headers_descriptions,
        body_description=body_description,
        analyze_headers=analyze_headers,
    )
    verification = description.verify(
        Response(
            id=sentinel.response_id,
            elapsed=sentinel.elapsed,
            status_code=200,
            headers={},
            body='{}',
            request_datetime=sentinel.request_datetime
        ),
        k='v',
    )
    assert verification.response_id == sentinel.response_id
    assert verification.status == Status.UNSTABLE
    assert verification.status_code.status == Status.SKIPPED
    assert verification.body.status == Status.UNSTABLE

    analyze_headers.assert_called_once_with({})
    for description in headers_descriptions:
        description.verify.assert_called_once_with(sentinel.headers, k='v')
    body_description.verify.assert_called_once_with('{}', k='v')


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
):
    status_code_predicates = [
        MagicMock(Predicate, verify=MagicMock(
            return_value=Verification(status=status_code_status)
        )),
    ]
    headers_descriptions = [
        MagicMock(Description, verify=MagicMock(
            return_value=Verification(status=headers_status)
        )),
    ]
    body_description = MagicMock(BodyDescription, verify=MagicMock(
        return_value=Verification(status=body_status)
    ))
    description = ResponseDescription(
        status_code_predicates=status_code_predicates,
        headers_descriptions=headers_descriptions,
        body_description=body_description,
    )
    verification = description.verify(
        Response(
            id=sentinel.response_id,
            elapsed=sentinel.elapsed,
            status_code=200,
            headers={},
            body='xxx',
            request_datetime=sentinel.request_datetime
        ),
    )
    assert verification.status == expected
