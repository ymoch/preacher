from unittest.mock import NonCallableMock, sentinel

from preacher.compilation.verification.matcher import MatcherFactoryCompiler
from preacher.compilation.verification.predicate import PredicateCompiler

PKG = "preacher.compilation.verification.predicate"


def test_matcher_predicate(mocker):
    matcher_factory = NonCallableMock(MatcherFactoryCompiler)
    matcher_factory.compile.return_value = sentinel.factory

    predicate_ctor = mocker.patch(f"{PKG}.MatcherWrappingPredicate")
    predicate_ctor.return_value = sentinel.predicate

    predicate = PredicateCompiler(matcher_factory).compile(sentinel.obj)
    assert predicate is sentinel.predicate

    matcher_factory.compile.assert_called_once_with(sentinel.obj)
    predicate_ctor.assert_called_once_with(sentinel.factory)
