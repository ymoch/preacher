from unittest.mock import MagicMock, sentinel

from pytest import fixture

from preacher.core.description import Description
from preacher.core.status import Status
from preacher.core.verification import Verification


@fixture
def extractor():
    return MagicMock(extract=MagicMock(return_value=sentinel.target))


def test_when_analysis_fails():
    extractor = MagicMock(extract=MagicMock(side_effect=Exception('message')))
    description = Description(extractor=extractor, predicates=[])
    verification = description(sentinel.analyzer)
    assert verification.status == Status.FAILURE
    assert verification.message == 'Exception: message'

    extractor.extract.assert_called_once_with(sentinel.analyzer)


def test_when_given_no_predicates(extractor):
    description = Description(extractor=extractor, predicates=[])
    verification = description(sentinel.analyzer)
    assert verification.status == Status.SKIPPED
    assert len(verification.children) == 0

    extractor.extract.assert_called_once_with(sentinel.analyzer)


def test_when_given_a_predicate_to_fail(extractor):
    description = Description(
        extractor=extractor,
        predicates=[
            MagicMock(return_value=Verification(Status.UNSTABLE)),
            MagicMock(return_value=Verification(Status.FAILURE)),
            MagicMock(return_value=Verification(Status.SUCCESS)),
        ]
    )
    verification = description(sentinel.analyzer, k='v')
    assert verification.status == Status.FAILURE
    assert len(verification.children) == 3
    assert verification.children[0].status == Status.UNSTABLE
    assert verification.children[1].status == Status.FAILURE
    assert verification.children[2].status == Status.SUCCESS

    extractor.extract.assert_called_once_with(sentinel.analyzer)
    description.predicates[0].assert_called_once_with(sentinel.target, k='v')
    description.predicates[1].assert_called_once_with(sentinel.target, k='v')
    description.predicates[2].assert_called_once_with(sentinel.target, k='v')


def test_when_given_predicates_to_success(extractor):
    description = Description(
        extractor=extractor,
        predicates=[
            MagicMock(return_value=Verification(Status.SUCCESS)),
            MagicMock(return_value=Verification(Status.SUCCESS)),
        ]
    )
    verification = description(sentinel.analyzer, k='v')
    assert verification.status == Status.SUCCESS
    assert len(verification.children) == 2
    assert verification.children[0].status == Status.SUCCESS
    assert verification.children[1].status == Status.SUCCESS

    extractor.extract.assert_called_once_with(sentinel.analyzer)
    description.predicates[0].assert_called_once_with(sentinel.target, k='v')
    description.predicates[1].assert_called_once_with(sentinel.target, k='v')
