from unittest.mock import sentinel

from preacher.compilation.verification.predicate import PredicateCompiler

PKG = 'preacher.compilation.verification.predicate'


def test_matcher_predicate(mocker):
    compile_hamcrest_factory = mocker.patch(f'{PKG}.compile_matcher_factory')
    compile_hamcrest_factory.return_value = sentinel.factory
    predicate_ctor = mocker.patch(f'{PKG}.MatcherWrappingPredicate')
    predicate_ctor.return_value = sentinel.predicate

    predicate = PredicateCompiler().compile(sentinel.obj)
    assert predicate == sentinel.predicate

    compile_hamcrest_factory.assert_called_once_with(sentinel.obj)
    predicate_ctor.assert_called_once_with(sentinel.factory)
