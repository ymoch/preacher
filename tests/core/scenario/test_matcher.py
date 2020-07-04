from typing import Optional
from unittest.mock import Mock, NonCallableMock, sentinel

from hamcrest.core.matcher import Matcher as HamcrestMatcher
from pytest import fixture, raises

from preacher.core.interpretation.error import InterpretationError
from preacher.core.interpretation.value import Value, ValueContext
from preacher.core.scenario.matcher import (
    Matcher,
    StaticMatcher,
    ValueMatcher,
    RecursiveMatcher,
    match,
)
from preacher.core.scenario.status import Status

PKG = 'preacher.core.scenario.matcher'


@fixture
def hamcrest_factory():
    return Mock(return_value=sentinel.hamcrest)


@fixture
def matcher():
    matcher = NonCallableMock(Matcher)
    matcher.to_hamcrest.return_value = sentinel.hamcrest
    return matcher


def test_matcher_interface():
    class IncompleteMatcher(Matcher):
        def to_hamcrest(
            self,
            context: Optional[ValueContext] = None,
        ) -> HamcrestMatcher:
            return super().to_hamcrest()

    matcher = IncompleteMatcher()
    with raises(NotImplementedError):
        matcher.to_hamcrest()


def test_static_matcher():
    matcher = StaticMatcher(sentinel.hamcrest)
    assert matcher.to_hamcrest() == sentinel.hamcrest


def test_value_matcher(hamcrest_factory):
    value = NonCallableMock(Value)
    value.resolve.return_value = sentinel.resolved

    matcher = ValueMatcher(hamcrest_factory, value)
    hamcrest = matcher.to_hamcrest(sentinel.context)

    assert hamcrest == sentinel.hamcrest
    value.resolve.assert_called_once_with(sentinel.context)
    hamcrest_factory.assert_called_once_with(sentinel.resolved)


def test_recursive_matcher(hamcrest_factory):
    inner_matchers = [
        NonCallableMock(Matcher, to_hamcrest=Mock(
            return_value=sentinel.inner_hamcrest_0
        )),
        NonCallableMock(Matcher, to_hamcrest=Mock(
            return_value=sentinel.inner_hamcrest_1
        )),
    ]

    matcher = RecursiveMatcher(hamcrest_factory, inner_matchers)
    hamcrest = matcher.to_hamcrest(sentinel.context)
    assert hamcrest == sentinel.hamcrest
    for inner_matcher in inner_matchers:
        inner_matcher.to_hamcrest.assert_called_once_with(sentinel.context)
    hamcrest_factory.assert_called_once_with(
        sentinel.inner_hamcrest_0,
        sentinel.inner_hamcrest_1,
    )


def test_match_when_an_interpretation_error_occurs():
    matcher = NonCallableMock(Matcher)
    matcher.to_hamcrest.side_effect = InterpretationError('interpretation')
    verification = match(matcher, sentinel.actual, sentinel.context)

    assert verification.status == Status.FAILURE
    assert verification.message == 'InterpretationError: interpretation'
    matcher.to_hamcrest.assert_called_once_with(sentinel.context)


def test_match_when_an_error_occurs_on_assertion(matcher, mocker):
    assert_that = mocker.patch(f'{PKG}.assert_that')
    assert_that.side_effect = RuntimeError('message')

    verification = match(matcher, sentinel.actual, sentinel.context)
    assert verification.status == Status.FAILURE
    assert verification.message == 'RuntimeError: message'
    matcher.to_hamcrest.assert_called_once_with(sentinel.context)
    assert_that.assert_called_once_with(sentinel.actual, sentinel.hamcrest)


def test_match_when_assertion_fails(matcher, mocker):
    assert_that = mocker.patch(f'{PKG}.assert_that')
    assert_that.side_effect = AssertionError('message')

    verification = match(matcher, sentinel.actual)
    assert verification.status == Status.UNSTABLE
    assert verification.message == 'message'
    matcher.to_hamcrest.assert_called_once_with(None)
    assert_that.assert_called_once_with(sentinel.actual, sentinel.hamcrest)


def test_match_when_the_assertion_succeeds(matcher, mocker):
    assert_that = mocker.patch(f'{PKG}.assert_that')

    verification = match(matcher, sentinel.actual)
    assert verification.status == Status.SUCCESS
    matcher.to_hamcrest.assert_called_once_with(None)
    assert_that.assert_called_once_with(sentinel.actual, sentinel.hamcrest)
