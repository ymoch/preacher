from unittest.mock import MagicMock, sentinel

from preacher.core.description import Description
from preacher.core.status import Status
from preacher.core.verification import Verification


def test_when_analysis_fails():
    description = Description(extraction=sentinel.extraction, predicates=[])
    analyzer = MagicMock(jq=MagicMock(side_effect=Exception('message')))
    verification = description(analyzer)
    assert verification.status == Status.FAILURE
    assert verification.message == 'Exception: message'

    analyzer.jq.assert_called_once_with(sentinel.extraction)


def test_when_given_no_predicates():
    description = Description(extraction=sentinel.extraction, predicates=[])
    analyzer = MagicMock()
    verification = description(analyzer)
    assert verification.status == Status.SKIPPED
    assert len(verification.children) == 0

    analyzer.jq.assert_called_once_with(sentinel.extraction)


def test_when_given_a_predicate_to_fail():
    description = Description(
        extraction=sentinel.extraction,
        predicates=[
            MagicMock(return_value=Verification(Status.UNSTABLE)),
            MagicMock(return_value=Verification(Status.FAILURE)),
            MagicMock(return_value=Verification(Status.SUCCESS)),
        ]
    )
    analyzer = MagicMock(jq=MagicMock(return_value=sentinel.target))
    verification = description(analyzer, k='v')
    assert verification.status == Status.FAILURE
    assert len(verification.children) == 3
    assert verification.children[0].status == Status.UNSTABLE
    assert verification.children[1].status == Status.FAILURE
    assert verification.children[2].status == Status.SUCCESS

    analyzer.jq.assert_called_once_with(sentinel.extraction)
    description.predicates[0].assert_called_once_with(sentinel.target, k='v')
    description.predicates[1].assert_called_once_with(sentinel.target, k='v')
    description.predicates[2].assert_called_once_with(sentinel.target, k='v')


def test_when_given_predicates_to_success():
    description = Description(
        extraction=sentinel.extraction,
        predicates=[
            MagicMock(return_value=Verification(Status.SUCCESS)),
            MagicMock(return_value=Verification(Status.SUCCESS)),
        ]
    )
    analyzer = MagicMock(jq=MagicMock(return_value=sentinel.target))
    verification = description(analyzer, k='v')
    assert verification.status == Status.SUCCESS
    assert len(verification.children) == 2
    assert verification.children[0].status == Status.SUCCESS
    assert verification.children[1].status == Status.SUCCESS

    analyzer.jq.assert_called_once_with(sentinel.extraction)
    description.predicates[0].assert_called_once_with(sentinel.target, k='v')
    description.predicates[1].assert_called_once_with(sentinel.target, k='v')
