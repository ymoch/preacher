from unittest.mock import MagicMock

from preacher.core.response_description import ResponseDescription
from preacher.core.status import Status
from preacher.core.verification import Verification


def test_when_given_no_description():
    description = ResponseDescription(
        status_code_predicates=[],
        body_descriptions=[],
    )
    verification = description(
        status_code=200,
        body='',
        key='value',
    )
    assert verification.status_code.status == Status.SKIPPED
    assert verification.body.status == Status.SKIPPED
    assert verification.status == Status.SKIPPED


def test_when_given_invalid_body():
    description = ResponseDescription(
        status_code_predicates=[
            MagicMock(return_value=Verification.succeed()),
        ],
        body_descriptions=[
            MagicMock(return_value=Verification.succeed()),
        ],
    )
    verification = description(
        status_code=200,
        body='invalid-format',
        key='value',
    )
    assert verification.status == Status.FAILURE
    assert verification.status_code.status == Status.SUCCESS
    assert verification.body.status == Status.FAILURE
    assert verification.body.message.startswith('JSONDecodeError:')

    description.status_code_predicates[0].assert_called_once_with(
        200,
        key='value',
    )
    description.body_descriptions[0].assert_not_called()


def test_when_given_descriptions():
    description = ResponseDescription(
        status_code_predicates=[],
        body_descriptions=[
            MagicMock(return_value=Verification(status=Status.UNSTABLE)),
            MagicMock(return_value=Verification.succeed()),
        ],
    )
    verification = description(
        status_code=200,
        body='{}',
        key='value',
    )
    assert verification.status == Status.UNSTABLE
    assert verification.status_code.status == Status.SKIPPED
    assert verification.body.status == Status.UNSTABLE
    assert verification.body.children[0].status == Status.UNSTABLE
    assert verification.body.children[1].status == Status.SUCCESS

    description.body_descriptions[0].assert_called_once_with(
        {},
        key='value',
    )
    description.body_descriptions[1].assert_called_once_with(
        {},
        key='value',
    )
