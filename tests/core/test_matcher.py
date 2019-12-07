from unittest.mock import MagicMock, patch, sentinel

from hamcrest.core.matcher import Matcher as HamcrestMatcher
from pytest import fixture, raises

from preacher.core.matcher import Matcher, match
from preacher.core.status import Status
from preacher.interpretation.error import InterpretationError

PACKAGE = 'preacher.core.matcher'


@fixture
def matcher():
    matcher = MagicMock(Matcher)
    matcher.to_hamcrest.return_value = sentinel.hamcrest
    return matcher


def test_matcher_interface():
    class IncompleteMatcher(Matcher):
        def to_hamcrest(self, **kwargs) -> HamcrestMatcher:
            return super().to_hamcrest()

    matcher = IncompleteMatcher()
    with raises(NotImplementedError):
        matcher.to_hamcrest()


def test_match_when_an_interpretation_error_occurs():
    matcher = MagicMock(Matcher)
    matcher.to_hamcrest.side_effect = InterpretationError('interpretation')
    verification = match(matcher, sentinel.actual, k='v')

    assert verification.status == Status.FAILURE
    assert verification.message == 'InterpretationError: interpretation'
    matcher.to_hamcrest.assert_called_once_with(k='v')


@patch(f'{PACKAGE}.assert_that', side_effect=RuntimeError('message'))
def test_match_when_an_error_occurs_on_assertion(assert_that, matcher):
    verification = match(matcher, sentinel.actual, key='value')

    assert verification.status == Status.FAILURE
    assert verification.message == 'RuntimeError: message'
    matcher.to_hamcrest.assert_called_once_with(key='value')
    assert_that.assert_called_once_with(sentinel.actual, sentinel.hamcrest)


@patch(f'{PACKAGE}.assert_that', side_effect=AssertionError('message'))
def test_match_when_assertion_fails(assert_that, matcher):
    verification = match(matcher, sentinel.actual)

    assert verification.status == Status.UNSTABLE
    assert verification.message == 'message'
    matcher.to_hamcrest.assert_called_once_with()
    assert_that.assert_called_once_with(sentinel.actual, sentinel.hamcrest)


@patch(f'{PACKAGE}.assert_that')
def test_match_when_the_assertion_succeeds(assert_that, matcher):
    verification = match(matcher, sentinel.actual)

    assert verification.status == Status.SUCCESS
    assert_that.assert_called_once_with(sentinel.actual, sentinel.hamcrest)
