from unittest.mock import patch, sentinel

from preacher.core.status import Status
from preacher.core.predicate import MatcherPredicate


PACKAGE = 'preacher.core.predicate'


@patch(f'{PACKAGE}.assert_that', side_effect=RuntimeError('message'))
def test_when_an_error_occurs(assert_that):
    predicate = MatcherPredicate(sentinel.matcher)
    verification = predicate(sentinel.actual)

    assert verification.status == Status.FAILURE
    assert verification.message == 'RuntimeError: message'
    assert_that.assert_called_once_with(sentinel.actual, sentinel.matcher)


@patch(f'{PACKAGE}.assert_that', side_effect=AssertionError('message'))
def test_when_the_assertion_fails(assert_that):
    predicate = MatcherPredicate(sentinel.matcher)
    verification = predicate(sentinel.actual)

    assert verification.status == Status.UNSTABLE
    assert verification.message == 'message'
    assert_that.assert_called_once_with(sentinel.actual, sentinel.matcher)


@patch(f'{PACKAGE}.assert_that')
def test_when_the_assertion_succeeds(assert_that):
    predicate = MatcherPredicate(sentinel.matcher)
    verification = predicate(sentinel.actual, k='v')

    assert verification.status == Status.SUCCESS
    assert_that.assert_called_once_with(sentinel.actual, sentinel.matcher)
