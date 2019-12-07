from datetime import datetime, timezone
from unittest.mock import patch, sentinel

from preacher.compilation.predicate import PredicateCompiler

PACKAGE = 'preacher.compilation.predicate'
REQUEST_DATETIME = datetime(2019, 8, 28, tzinfo=timezone.utc)


@patch(f'{PACKAGE}.compile_matcher', return_value=sentinel.matcher)
@patch(f'{PACKAGE}.MatcherPredicate', return_value=sentinel.predicate)
def test_matcher_predicate(predicate_ctor, compile_matcher):
    predicate = PredicateCompiler().compile(sentinel.obj)
    assert predicate == sentinel.predicate

    compile_matcher.assert_called_once_with(sentinel.obj)
    predicate_ctor.assert_called_once_with(sentinel.matcher)
