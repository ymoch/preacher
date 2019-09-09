from unittest.mock import MagicMock, patch, sentinel

from pytest import fixture

from preacher.core.predicate import DynamicMatcherPredicate
from preacher.core.status import Status


PACKAGE = 'preacher.core.predicate'


@fixture
def matcher_factory():
    return MagicMock(return_value=sentinel.matcher)


@fixture
def converter():
    return MagicMock(return_value=sentinel.predicated_value)


def test_when_matcher_creation_fails():
    matcher_factory = MagicMock(side_effect=RuntimeError('message'))

    predicate = DynamicMatcherPredicate(matcher_factory=matcher_factory)
    result = predicate('x')
    assert result.status == Status.FAILURE


def test_when_conversion_fails(matcher_factory):
    converter = MagicMock(side_effect=RuntimeError('message'))

    predicate = DynamicMatcherPredicate(
        matcher_factory=matcher_factory,
        converter=converter,
    )
    result = predicate('x')
    assert result.status == Status.FAILURE


@patch(f'{PACKAGE}.MatcherPredicate')
def test_given_no_converter(matcher_predicate_ctor, matcher_factory):
    matcher_predicate = MagicMock(return_value=sentinel.verification)
    matcher_predicate_ctor.return_value = matcher_predicate

    predicate = DynamicMatcherPredicate(matcher_factory=matcher_factory)
    result = predicate('x', key='value')
    assert result == sentinel.verification

    matcher_factory.assert_called_once_with(key='value')
    matcher_predicate_ctor.assert_called_once_with(sentinel.matcher)
    matcher_predicate.assert_called_once_with('x', key='value')


@patch(f'{PACKAGE}.MatcherPredicate')
def test_given_converter(matcher_predicate_ctor, matcher_factory, converter):
    matcher_predicate = MagicMock(return_value=sentinel.verification)
    matcher_predicate_ctor.return_value = matcher_predicate

    predicate = DynamicMatcherPredicate(
        matcher_factory=matcher_factory,
        converter=converter,
    )
    result = predicate('x', key='value')
    assert result == sentinel.verification

    matcher_factory.assert_called_once_with(key='value')
    converter.assert_called_once_with('x')
    matcher_predicate_ctor.assert_called_once_with(sentinel.matcher)
    matcher_predicate.assert_called_once_with(
        sentinel.predicated_value, key='value')
