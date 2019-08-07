from unittest.mock import MagicMock, sentinel

from preacher.core.description import Description
from preacher.core.status import Status
from preacher.core.verification import Verification


def test_when_extraction_fails():
    description = Description(
        extraction=MagicMock(side_effect=Exception('message')),
        predicates=[],
    )
    verification = description('described')
    assert verification.status == Status.FAILURE
    assert verification.message == 'Exception: message'


def test_when_given_no_predicates():
    description = Description(
        extraction=MagicMock(return_value=sentinel.target),
        predicates=[],
    )
    verification = description('described')
    assert verification.status == Status.SKIPPED
    assert len(verification.children) == 0


def test_when_given_a_predicate_to_fail():
    description = Description(
        extraction=MagicMock(return_value=sentinel.target),
        predicates=[
            MagicMock(return_value=Verification(Status.UNSTABLE)),
            MagicMock(return_value=Verification(Status.FAILURE)),
            MagicMock(return_value=Verification(Status.SUCCESS)),
        ]
    )
    verification = description('described')
    assert verification.status == Status.FAILURE
    assert len(verification.children) == 3
    assert verification.children[0].status == Status.UNSTABLE
    assert verification.children[1].status == Status.FAILURE
    assert verification.children[2].status == Status.SUCCESS


def test_when_given_predicates_to_success():
    description = Description(
        extraction=MagicMock(return_value='target'),
        predicates=[
            MagicMock(return_value=Verification(Status.SUCCESS)),
            MagicMock(return_value=Verification(Status.SUCCESS)),
        ]
    )
    verification = description('described')
    assert verification.status == Status.SUCCESS
    assert len(verification.children) == 2
    assert verification.children[0].status == Status.SUCCESS
    assert verification.children[1].status == Status.SUCCESS
