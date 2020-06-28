from typing import Optional, Any
from unittest.mock import sentinel

from pytest import raises

from preacher.core.scenario.predicate import MatcherPredicate, Predicate
from preacher.core.scenario.verification import Verification

PKG = 'preacher.core.scenario.predicate'


def test_predicate_interface():
    class IncompletePredicate(Predicate):
        def verify(self, actual: Optional[Any], **kwargs) -> Verification:
            return super().verify(actual, **kwargs)

    with raises(NotImplementedError):
        IncompletePredicate().verify(sentinel.actual, key='value')


def test_matcher_predicate(mocker):
    match = mocker.patch(f'{PKG}.match', return_value=sentinel.verification)

    predicate = MatcherPredicate(sentinel.matcher)
    verification = predicate.verify(sentinel.actual, key='value')

    assert verification == sentinel.verification
    match.assert_called_once_with(
        sentinel.matcher,
        sentinel.actual,
        key='value',
    )
