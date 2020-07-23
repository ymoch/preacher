from typing import Optional
from unittest.mock import Mock, NonCallableMock, sentinel

from hamcrest.core.matcher import Matcher as HamcrestMatcher
from pytest import fixture, raises

from preacher.core.status import Status
from preacher.core.value import Value, ValueContext
from preacher.core.verification.matcher import (
    HamcrestFactory,
    StaticMatcher,
    ValueMatcher,
    RecursiveMatcher,
    match,
)

PKG = 'preacher.core.verification.matcher'


@fixture
def hamcrest_factory():
    return Mock(return_value=sentinel.hamcrest)


@fixture
def matcher():
    matcher = NonCallableMock(HamcrestFactory)
    matcher.create.return_value = sentinel.hamcrest
    return matcher


def test_matcher_interface():
    class IncompleteMatcher(HamcrestFactory):
        def create(
            self,
            context: Optional[ValueContext] = None,
        ) -> HamcrestMatcher:
            return super().create()

    matcher = IncompleteMatcher()
    with raises(NotImplementedError):
        matcher.create()


def test_static_matcher():
    matcher = StaticMatcher(sentinel.hamcrest)
    assert matcher.create() == sentinel.hamcrest


def test_value_matcher(hamcrest_factory):
    value = NonCallableMock(Value)
    value.resolve.return_value = sentinel.resolved

    matcher = ValueMatcher(hamcrest_factory, value)
    hamcrest = matcher.create(sentinel.context)

    assert hamcrest == sentinel.hamcrest
    value.resolve.assert_called_once_with(sentinel.context)
    hamcrest_factory.assert_called_once_with(sentinel.resolved)


def test_recursive_matcher(hamcrest_factory):
    inner_matchers = [
        NonCallableMock(HamcrestFactory, create=Mock(
            return_value=sentinel.inner_hamcrest_0
        )),
        NonCallableMock(HamcrestFactory, create=Mock(
            return_value=sentinel.inner_hamcrest_1
        )),
    ]

    matcher = RecursiveMatcher(hamcrest_factory, inner_matchers)
    hamcrest = matcher.create(sentinel.context)
    assert hamcrest == sentinel.hamcrest
    for inner_matcher in inner_matchers:
        inner_matcher.create.assert_called_once_with(sentinel.context)
    hamcrest_factory.assert_called_once_with(
        sentinel.inner_hamcrest_0,
        sentinel.inner_hamcrest_1,
    )


def test_match_when_an_error_occurs():
    matcher = NonCallableMock(HamcrestFactory)
    matcher.create.side_effect = TypeError('typing')
    verification = match(matcher, sentinel.actual, sentinel.context)

    assert verification.status == Status.FAILURE
    assert verification.message == 'TypeError: typing'
    matcher.create.assert_called_once_with(sentinel.context)


def test_match_when_an_error_occurs_on_assertion(matcher, mocker):
    assert_that = mocker.patch(f'{PKG}.assert_that')
    assert_that.side_effect = RuntimeError('message')

    verification = match(matcher, sentinel.actual, sentinel.context)
    assert verification.status == Status.FAILURE
    assert verification.message == 'RuntimeError: message'
    matcher.create.assert_called_once_with(sentinel.context)
    assert_that.assert_called_once_with(sentinel.actual, sentinel.hamcrest)


def test_match_when_assertion_fails(matcher, mocker):
    assert_that = mocker.patch(f'{PKG}.assert_that')
    assert_that.side_effect = AssertionError('message')

    verification = match(matcher, sentinel.actual)
    assert verification.status == Status.UNSTABLE
    assert verification.message == 'message'
    matcher.create.assert_called_once_with(None)
    assert_that.assert_called_once_with(sentinel.actual, sentinel.hamcrest)


def test_match_when_the_assertion_succeeds(matcher, mocker):
    assert_that = mocker.patch(f'{PKG}.assert_that')

    verification = match(matcher, sentinel.actual)
    assert verification.status == Status.SUCCESS
    matcher.create.assert_called_once_with(None)
    assert_that.assert_called_once_with(sentinel.actual, sentinel.hamcrest)
