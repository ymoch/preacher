from typing import Optional
from unittest.mock import NonCallableMock, sentinel

from pytest import raises

from preacher.core.value import ValueContext
from preacher.core.verification.matcher import Matcher
from preacher.core.verification.predicate import Predicate, MatcherPredicate
from preacher.core.verification.verification import Verification

PKG = 'preacher.core.verification.predicate'


def test_predicate_interface():
    class IncompletePredicate(Predicate):
        def verify(
            self,
            actual: object,
            context: Optional[ValueContext] = None,
        ) -> Verification:
            return super().verify(actual, context)

    with raises(NotImplementedError):
        IncompletePredicate().verify(sentinel.actual)


def test_matcher_predicate():
    matcher = NonCallableMock(Matcher)
    matcher.match.return_value = sentinel.verification

    predicate = MatcherPredicate(matcher)
    verification = predicate.verify(sentinel.actual, sentinel.context)
    assert verification is sentinel.verification

    matcher.match.assert_called_once_with(sentinel.actual, sentinel.context)
