from unittest.mock import sentinel

from preacher.compilation.verification.predicate import PredicateCompiler

PKG = 'preacher.compilation.verification.predicate'


def test_matcher_predicate(mocker):
    compile_matcher = mocker.patch(f'{PKG}.compile_matcher')
    compile_matcher.return_value = sentinel.matcher
    predicate_ctor = mocker.patch(f'{PKG}.MatcherPredicate')
    predicate_ctor.return_value = sentinel.predicate

    predicate = PredicateCompiler().compile(sentinel.obj)
    assert predicate == sentinel.predicate

    compile_matcher.assert_called_once_with(sentinel.obj)
    predicate_ctor.assert_called_once_with(sentinel.matcher)
