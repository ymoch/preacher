from typing import Optional
from unittest.mock import Mock, NonCallableMock, sentinel

from hamcrest.core.matcher import Matcher as HamcrestMatcher
from pytest import fixture, raises

from preacher.core.status import Status
from preacher.core.value import Value, ValueContext
from preacher.core.verification.matcher import HamcrestFactory
from preacher.core.verification.matcher import HamcrestWrappingMatcher
from preacher.core.verification.matcher import Matcher
from preacher.core.verification.matcher import RecursiveHamcrestFactory
from preacher.core.verification.matcher import StaticHamcrestFactory
from preacher.core.verification.matcher import ValueHamcrestFactory
from preacher.core.verification.verification import Verification

PKG = 'preacher.core.verification.matcher'


def test_matcher_interface():
    class _Incomplete(Matcher):
        def match(self, actual: object, context: Optional[ValueContext] = None) -> Verification:
            return super().match(actual, context)

    matcher = _Incomplete()
    with raises(NotImplementedError):
        matcher.match(sentinel.actual, None)


def test_hamcrest_factory_interface():
    class IncompleteMatcher(HamcrestFactory):
        def create(
            self,
            context: Optional[ValueContext] = None,
        ) -> HamcrestMatcher:
            return super().create()

    matcher = IncompleteMatcher()
    with raises(NotImplementedError):
        matcher.create()


@fixture
def hamcrest_factory():
    return Mock(return_value=sentinel.hamcrest)


def test_static_factory():
    matcher = StaticHamcrestFactory(sentinel.hamcrest)
    assert matcher.create() == sentinel.hamcrest


def test_value_factory(hamcrest_factory):
    value = NonCallableMock(Value)
    value.resolve.return_value = sentinel.resolved

    matcher = ValueHamcrestFactory(hamcrest_factory, value)
    hamcrest = matcher.create(sentinel.context)

    assert hamcrest == sentinel.hamcrest
    value.resolve.assert_called_once_with(sentinel.context)
    hamcrest_factory.assert_called_once_with(sentinel.resolved)


def test_recursive_factory(hamcrest_factory):
    inner_matchers = [
        NonCallableMock(HamcrestFactory, create=Mock(
            return_value=sentinel.inner_hamcrest_0
        )),
        NonCallableMock(HamcrestFactory, create=Mock(
            return_value=sentinel.inner_hamcrest_1
        )),
    ]

    matcher = RecursiveHamcrestFactory(hamcrest_factory, inner_matchers)
    hamcrest = matcher.create(sentinel.context)
    assert hamcrest == sentinel.hamcrest
    for inner_matcher in inner_matchers:
        inner_matcher.create.assert_called_once_with(sentinel.context)
    hamcrest_factory.assert_called_once_with(
        sentinel.inner_hamcrest_0,
        sentinel.inner_hamcrest_1,
    )


@fixture
def factory():
    factory = NonCallableMock(HamcrestFactory)
    factory.create.return_value = sentinel.hamcrest
    return factory


@fixture
def matcher(factory):
    return HamcrestWrappingMatcher(factory)


def test_match_when_an_error_occurs(matcher, factory):
    factory.create.side_effect = TypeError('typing')

    verification = matcher.match(sentinel.actual, sentinel.context)
    assert verification.status == Status.FAILURE
    assert verification.message == 'TypeError: typing'
    factory.create.assert_called_once_with(sentinel.context)


def test_match_when_an_error_occurs_on_assertion(mocker, matcher, factory):
    assert_that = mocker.patch(f'{PKG}.assert_that')
    assert_that.side_effect = RuntimeError('message')

    verification = matcher.match(sentinel.actual, sentinel.context)
    assert verification.status == Status.FAILURE
    assert verification.message == 'RuntimeError: message'
    factory.create.assert_called_once_with(sentinel.context)
    assert_that.assert_called_once_with(sentinel.actual, sentinel.hamcrest)


def test_match_when_assertion_fails(mocker, matcher, factory):
    assert_that = mocker.patch(f'{PKG}.assert_that')
    assert_that.side_effect = AssertionError('message')

    verification = matcher.match(sentinel.actual)
    assert verification.status == Status.UNSTABLE
    assert verification.message == 'message'
    factory.create.assert_called_once_with(None)
    assert_that.assert_called_once_with(sentinel.actual, sentinel.hamcrest)


def test_match_when_the_assertion_succeeds(mocker, matcher, factory):
    assert_that = mocker.patch(f'{PKG}.assert_that')

    verification = matcher.match(sentinel.actual)
    assert verification.status == Status.SUCCESS
    factory.create.assert_called_once_with(None)
    assert_that.assert_called_once_with(sentinel.actual, sentinel.hamcrest)
