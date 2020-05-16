from unittest.mock import MagicMock, patch, sentinel

from hamcrest.core.matcher import Matcher as HamcrestMatcher
from pytest import fixture, raises

from preacher.core.interpretation.error import InterpretationError
from preacher.core.interpretation.value import Value
from preacher.core.scenario.matcher import (
    Matcher,
    StaticMatcher,
    ValueMatcher,
    RecursiveMatcher,
    match,
)
from preacher.core.scenario.status import Status

PACKAGE = 'preacher.core.scenario.matcher'


@fixture
def hamcrest_factory():
    return MagicMock(return_value=sentinel.hamcrest)


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


def test_static_matcher():
    matcher = StaticMatcher(sentinel.hamcrest)
    assert matcher.to_hamcrest(k='v') == sentinel.hamcrest


def test_value_matcher(hamcrest_factory):
    value = MagicMock(Value)
    value.apply_context.return_value = sentinel.value_in_context

    matcher = ValueMatcher(hamcrest_factory, value)
    hamcrest = matcher.to_hamcrest(key='value')

    assert hamcrest == sentinel.hamcrest
    value.apply_context.assert_called_once_with(key='value')
    hamcrest_factory.assert_called_once_with(sentinel.value_in_context)


def test_recursive_matcher(hamcrest_factory):
    inner_matchers = [
        MagicMock(Matcher, to_hamcrest=MagicMock(
            return_value=sentinel.inner_hamcrest_0
        )),
        MagicMock(Matcher, to_hamcrest=MagicMock(
            return_value=sentinel.inner_hamcrest_1
        )),
    ]

    matcher = RecursiveMatcher(hamcrest_factory, inner_matchers)
    hamcrest = matcher.to_hamcrest(key='value')
    assert hamcrest == sentinel.hamcrest
    for inner_matcher in inner_matchers:
        inner_matcher.to_hamcrest.assert_called_once_with(key='value')
        inner_matcher.to_hamcrest.assert_called_once_with(key='value')
    hamcrest_factory.assert_called_once_with(
        sentinel.inner_hamcrest_0,
        sentinel.inner_hamcrest_1,
    )


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
