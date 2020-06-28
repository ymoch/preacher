from datetime import datetime, timezone
from unittest.mock import sentinel

from preacher.compilation.predicate import PredicateCompiler

PACKAGE = 'preacher.compilation.predicate'
REQUEST_DATETIME = datetime(2019, 8, 28, tzinfo=timezone.utc)


def test_matcher_predicate(mocker):
    compile_matcher = mocker.patch(f'{PACKAGE}.compile_matcher')
    compile_matcher.return_value = sentinel.matcher
    predicate_ctor = mocker.patch(f'{PACKAGE}.MatcherPredicate')
    predicate_ctor.return_value = sentinel.predicate

    predicate = PredicateCompiler().compile(sentinel.obj)
    assert predicate == sentinel.predicate

    compile_matcher.assert_called_once_with(sentinel.obj)
    predicate_ctor.assert_called_once_with(sentinel.matcher)
