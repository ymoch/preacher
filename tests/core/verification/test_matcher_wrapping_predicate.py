from unittest.mock import sentinel, NonCallableMock

from pytest import fixture

from preacher.core.status import Status
from preacher.core.verification import MatcherWrappingPredicate, MatcherFactory

PKG = "preacher.core.verification.matcher"


@fixture
def predicate(factory):
    return MatcherWrappingPredicate(factory)


@fixture
def factory():
    factory = NonCallableMock(MatcherFactory)
    factory.create.return_value = sentinel.matcher
    return factory


def test_match_when_matcher_creation_fails(predicate, factory):
    factory.create.side_effect = TypeError("typing")

    verification = predicate.verify(sentinel.actual, sentinel.context)
    assert verification.status == Status.FAILURE
    assert verification.message == "TypeError: typing"
    factory.create.assert_called_once_with(sentinel.context)


def test_match_when_an_error_occurs_on_assertion(mocker, predicate, factory):
    assert_that = mocker.patch(f"{PKG}.assert_that")
    assert_that.side_effect = RuntimeError("message")

    verification = predicate.verify(sentinel.actual, sentinel.context)
    assert verification.status == Status.FAILURE
    assert verification.message == "RuntimeError: message"
    factory.create.assert_called_once_with(sentinel.context)
    assert_that.assert_called_once_with(sentinel.actual, sentinel.matcher)


def test_match_when_assertion_fails(mocker, predicate, factory):
    assert_that = mocker.patch(f"{PKG}.assert_that")
    assert_that.side_effect = AssertionError("message")

    verification = predicate.verify(sentinel.actual)
    assert verification.status == Status.UNSTABLE
    assert verification.message == "message"
    factory.create.assert_called_once_with(None)
    assert_that.assert_called_once_with(sentinel.actual, sentinel.matcher)


def test_match_when_the_assertion_succeeds(mocker, predicate, factory):
    assert_that = mocker.patch(f"{PKG}.assert_that")

    verification = predicate.verify(sentinel.actual)
    assert verification.status == Status.SUCCESS
    factory.create.assert_called_once_with(None)
    assert_that.assert_called_once_with(sentinel.actual, sentinel.matcher)
