from typing import Optional
from unittest.mock import sentinel

from pytest import raises

from preacher.core.value import ValueContext
from preacher.core.verification.predicate import Predicate
from preacher.core.verification.verification import Verification

PKG = 'preacher.core.verification.predicate'


def test_predicate_interface():
    class IncompletePredicate(Predicate):
        def verify(self, actual: object, context: Optional[ValueContext] = None) -> Verification:
            return super().verify(actual, context)

    with raises(NotImplementedError):
        IncompletePredicate().verify(sentinel.actual)
