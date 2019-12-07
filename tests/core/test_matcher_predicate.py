from unittest.mock import patch, sentinel

from preacher.core.predicate import MatcherPredicate

PACKAGE = 'preacher.core.predicate'


@patch(f'{PACKAGE}.match', return_value=sentinel.verification)
def test_matcher_predicate(match):
    predicate = MatcherPredicate(sentinel.matcher)
    verification = predicate(sentinel.actual, key='value')

    assert verification == sentinel.verification
    match.assert_called_once_with(
        sentinel.matcher,
        sentinel.actual,
        key='value',
    )
