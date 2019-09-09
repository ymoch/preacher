from unittest.mock import MagicMock

from pytest import mark

from preacher.core.response_description import ResponseDescription
from preacher.core.status import Status
from preacher.core.verification import Verification


def test_when_given_no_description():
    description = ResponseDescription()
    verification = description(status_code=200, headers={}, body='xxx')
    assert verification.status_code.status == Status.SKIPPED
    assert verification.body.status == Status.SKIPPED
    assert verification.status == Status.SKIPPED


def test_when_header_verification_fails():
    headers_descs = [MagicMock(side_effect=RuntimeError('message'))]
    description = ResponseDescription(headers_descriptions=headers_descs)

    verification = description(status_code=200, headers={}, body='xxx')
    assert verification.headers.status == Status.FAILURE


def test_when_given_invalid_body():
    status_code_predicates = [MagicMock(return_value=Verification.succeed())]
    body_descriptions = [MagicMock(return_value=Verification.succeed())]
    description = ResponseDescription(
        status_code_predicates=status_code_predicates,
        body_descriptions=body_descriptions,
    )
    verification = description(status_code=200, headers={}, body='xxx', k='v')
    assert verification.status == Status.FAILURE
    assert verification.status_code.status == Status.SUCCESS
    assert verification.body.status == Status.FAILURE
    assert verification.body.message.startswith('JSONDecodeError:')

    status_code_predicates[0].assert_called_once_with(200, k='v')
    body_descriptions[0].assert_not_called()


def test_when_given_descriptions():
    headers_descriptions = [
        MagicMock(return_value=Verification(status=Status.UNSTABLE)),
        MagicMock(return_value=Verification.succeed()),
    ]
    body_descriptions = [
        MagicMock(return_value=Verification(status=Status.UNSTABLE)),
        MagicMock(return_value=Verification.succeed()),
    ]
    description = ResponseDescription(
        status_code_predicates=[],
        headers_descriptions=headers_descriptions,
        body_descriptions=body_descriptions,
    )
    verification = description(status_code=200, headers={}, body='{}', k='v')
    assert verification.status == Status.UNSTABLE
    assert verification.status_code.status == Status.SKIPPED
    assert verification.body.status == Status.UNSTABLE
    assert verification.body.children[0].status == Status.UNSTABLE
    assert verification.body.children[1].status == Status.SUCCESS

    body_descriptions[0].assert_called_once_with({}, k='v')
    body_descriptions[1].assert_called_once_with({}, k='v')


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
        MagicMock(return_value=Verification(status=status_code_status)),
    ]
    headers_descriptions = [
        MagicMock(return_value=Verification(status=headers_status)),
    ]
    body_descriptions = [
        MagicMock(return_value=Verification(status=body_status)),
    ]
    description = ResponseDescription(
        status_code_predicates=status_code_predicates,
        headers_descriptions=headers_descriptions,
        body_descriptions=body_descriptions,
    )
    verification = description(status_code=200, headers={}, body='{}')
    assert verification.status == expected
