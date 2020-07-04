from unittest.mock import Mock, NonCallableMock, sentinel

from pytest import fixture

from preacher.core.scenario import Extractor
from preacher.core.scenario.description import Description
from preacher.core.scenario.predicate import Predicate
from preacher.core.scenario.status import Status
from preacher.core.scenario.verification import Verification


@fixture
def extractor():
    return NonCallableMock(
        spec=Extractor,
        extract=Mock(return_value=sentinel.target),
    )


def test_when_analysis_fails(extractor):
    extractor.extract.side_effect = Exception('message')

    description = Description(extractor=extractor, predicates=[])
    verification = description.verify(sentinel.analyzer)
    assert verification.status == Status.FAILURE
    assert verification.message == 'Exception: message'

    extractor.extract.assert_called_once_with(sentinel.analyzer)


def test_when_given_no_predicates(extractor):
    description = Description(extractor=extractor, predicates=[])
    verification = description.verify(sentinel.analyzer)
    assert verification.status is Status.SKIPPED
    assert len(verification.children) == 0

    extractor.extract.assert_called_once_with(sentinel.analyzer)


def test_when_given_predicates(extractor):
    predicate_results = [
        Verification(Status.UNSTABLE),
        Verification(Status.SUCCESS)
    ]
    predicates = [
        NonCallableMock(Predicate, verify=Mock(return_value=result))
        for result in predicate_results
    ]
    description = Description(extractor=extractor, predicates=predicates)
    verification = description.verify(sentinel.analyzer, sentinel.context)
    assert verification.status is Status.UNSTABLE
    assert len(verification.children) == 2
    assert verification.children[0].status == Status.UNSTABLE
    assert verification.children[1].status == Status.SUCCESS

    extractor.extract.assert_called_once_with(sentinel.analyzer)
    for predicate in predicates:
        predicate.verify.assert_called_once_with(
            sentinel.target,
            sentinel.context,
        )
