from datetime import datetime, timedelta, timezone
from unittest.mock import sentinel

from pytest import mark, raises

from preacher.compilation.error import CompilationError
from preacher.compilation.matcher import compile_matcher
from preacher.core.hamcrest import after, before
from preacher.core.scenario import Status
from preacher.core.scenario.matcher import match

PKG = 'preacher.compilation.matcher'

SUCCESS = Status.SUCCESS
UNSTABLE = Status.UNSTABLE
FAILURE = Status.FAILURE

NOW = datetime(2020, 5, 16, 12, 34, 56, tzinfo=timezone.utc)


@mark.parametrize('obj', [
    {},
    {'key1': 'value1', 'key2': 'value2'},
])
def test_invalid_mapping(obj):
    with raises(CompilationError):
        compile_matcher(obj)


@mark.parametrize(('obj', 'verified', 'expected_status'), [
    ('_undefined_string', 1, UNSTABLE),
    ('_undefined_string', 'value', UNSTABLE),
    ('_undefined_string', '_undefined_string', SUCCESS),
    ({'_undefined_key': 'value'}, None, UNSTABLE),
    ({'_undefined_key': 'value'}, 0, UNSTABLE),
    ({'_undefined_key': 'value'}, 'value', UNSTABLE),
    ({'_undefined_key': 'value'}, {'key': 'value'}, UNSTABLE),
    ({'_undefined_key': 'value'}, {'_undefined_key': '_'}, UNSTABLE),
    ({'_undefined_key': 'value'}, {'_undefined_key': 'value'}, SUCCESS),
    ('be_null', None, SUCCESS),
    ('be_null', False, UNSTABLE),
    ('not_be_null', None, UNSTABLE),
    ('not_be_null', False, SUCCESS),
    ('be_empty', None, UNSTABLE),
    ('be_empty', 0, UNSTABLE),
    ('be_empty', '', SUCCESS),
    ('be_empty', 'A', UNSTABLE),
    ('be_empty', [], SUCCESS),
    ('be_empty', [0], UNSTABLE),
    ({'have_length': 1}, None, UNSTABLE),
    ({'have_length': 1}, 1, UNSTABLE),
    ({'have_length': 1}, '', UNSTABLE),
    ({'have_length': 1}, [], UNSTABLE),
    ({'have_length': {'be_less_than': 1}}, [0], UNSTABLE),
    ({'have_length': 1}, 'A', SUCCESS),
    ({'have_length': 1}, [0], SUCCESS),
    ({'have_length': {'be_less_than': 2}}, [0], SUCCESS),
    ({'have_length': None}, [0], UNSTABLE),  # HACK: should be FAILURE
    ({'have_length': '1'}, [0], UNSTABLE),  # HACK: should be FAILURE
    ({'equal': 1}, 0, UNSTABLE),
    ({'equal': 1}, 1, SUCCESS),
    ({'equal': 1}, '1', UNSTABLE),
    ({'be_greater_than': 0}, -1, UNSTABLE),
    ({'be_greater_than': 0}, 0, UNSTABLE),
    ({'be_greater_than': 0}, 1, SUCCESS),
    ({'be_greater_than_or_equal_to': 0}, -1, UNSTABLE),
    ({'be_greater_than_or_equal_to': 0}, 0, SUCCESS),
    ({'be_greater_than_or_equal_to': 0}, 1, SUCCESS),
    ({'be_less_than': 0}, -1, SUCCESS),
    ({'be_less_than': 0}, 0, UNSTABLE),
    ({'be_less_than': 0}, 1, UNSTABLE),
    ({'be_less_than_or_equal_to': 0}, -1, SUCCESS),
    ({'be_less_than_or_equal_to': 0}, 0, SUCCESS),
    ({'be_less_than_or_equal_to': 0}, 1, UNSTABLE),
    ({'contain_string': '0'}, 0, UNSTABLE),
    ({'contain_string': '0'}, '123', UNSTABLE),
    ({'contain_string': '0'}, '21012', SUCCESS),
    ({'contain_string': 0}, '0', FAILURE),
    ({'start_with': 'AB'}, 0, UNSTABLE),
    ({'start_with': 'AB'}, 'ABC', SUCCESS),
    ({'start_with': 'AB'}, 'CAB', UNSTABLE),
    ({'start_with': 0}, '0', FAILURE),
    ({'end_with': 'BC'}, 0, UNSTABLE),
    ({'end_with': 'BC'}, 'ABC', SUCCESS),
    ({'end_with': 'BC'}, 'BCA', UNSTABLE),
    ({'end_with': 0}, '0', FAILURE),
    ({'match_regexp': '^A*B$'}, 'ACB', UNSTABLE),
    ({'match_regexp': '^A*B$'}, 'B', SUCCESS),
    ({'match_regexp': '^A*B$'}, 0, FAILURE),  # HACK: should be UNSTABLE.
    ({'match_regexp': 0}, '0', FAILURE),
    ({'be': 1}, 0, UNSTABLE),
    ({'be': 1}, '1', UNSTABLE),
    ({'be': 1}, 1, SUCCESS),
    ({'not': 1}, 'A', SUCCESS),
    ({'not': 1}, 0, SUCCESS),
    ({'not': 1}, 1, UNSTABLE),
    ({'not': {'be_greater_than': 0}}, -1, SUCCESS),
    ({'not': {'be_greater_than': 0}}, 0, SUCCESS),
    ({'not': {'be_greater_than': 0}}, 1, UNSTABLE),
    ({'have_item': {'equal': 1}}, None, UNSTABLE),
    ({'have_item': {'equal': 1}}, [], UNSTABLE),
    ({'have_item': {'equal': 1}}, [0, 'A'], UNSTABLE),
    ({'have_item': {'equal': 1}}, [0, 1, 2], SUCCESS),
    ({'contain': 1}, [], UNSTABLE),
    ({'contain': 1}, [1], SUCCESS),
    ({'contain_exactly': 1}, [1], SUCCESS),
    ({'contain': 1}, [1, 2], UNSTABLE),
    ({'contain': 1}, [2, 3], UNSTABLE),
    ({'contain': [1, {'be_greater_than': 2}, {'be_less_than': 3}]},
     [], UNSTABLE),
    ({'contain': [1, {'be_greater_than': 2}, {'be_less_than': 3}]},
     [1], UNSTABLE),
    ({'contain': [1, {'be_greater_than': 2}, {'be_less_than': 3}]},
     [1, 2, 4], UNSTABLE),
    ({'contain': [1, {'be_greater_than': 2}, {'be_less_than': 3}]},
     [1, 4, 2], SUCCESS),
    ({'contain': [1, {'be_greater_than': 2}, {'be_less_than': 3}]},
     [1, 4, 2, 3], UNSTABLE),
    ({'contain_in_any_order':
        [1, {'be_greater_than': 2}, {'be_less_than': 3}]},
     [], UNSTABLE),
    ({'contain_in_any_order':
        [1, {'be_greater_than': 2}, {'be_less_than': 3}]},
     [1], UNSTABLE),
    ({'contain_in_any_order':
        [1, {'be_greater_than': 2}, {'be_less_than': 3}]},
     [1, 2, 4], SUCCESS),
    ({'contain_in_any_order':
        [1, {'be_greater_than': 2}, {'be_less_than': 3}]},
     [4, 1, 2], SUCCESS),
    ({'contain_in_any_order':
        [1, {'be_greater_than': 2}, {'be_less_than': 3}]},
     [1, 4, 2], SUCCESS),
    ({'contain_in_any_order':
        [1, {'be_greater_than': 2}, {'be_less_than': 3}]},
     [1, 4, 2, 3], UNSTABLE),
    ({'have_items': [1, {'be_greater_than': 2}, {'be_less_than': 3}]},
     [], UNSTABLE),
    ({'have_items': [1, {'be_greater_than': 2}, {'be_less_than': 3}]},
     [1], UNSTABLE),
    ({'have_items': [1, {'be_greater_than': 2}, {'be_less_than': 3}]},
     [1, 2, 4], SUCCESS),
    ({'have_items': [1, {'be_greater_than': 2}, {'be_less_than': 3}]},
     [4, 1, 2], SUCCESS),
    ({'have_items': [1, {'be_greater_than': 2}, {'be_less_than': 3}]},
     [1, 4, 2], SUCCESS),
    ({'have_items': [1, {'be_greater_than': 2}, {'be_less_than': 3}]},
     [1, 4, 2, 3], SUCCESS),
    ({'all_of': [{'be_greater_than': 1}, {'be_less_than': 3}]}, 1, UNSTABLE),
    ({'all_of': [{'be_greater_than': 1}, {'be_less_than': 3}]}, 2, SUCCESS),
    ({'all_of': [{'be_greater_than': 1}, {'be_less_than': 3}]}, 3, UNSTABLE),
    ({'any_of': [{'be_less_than': 2}, {'be_greater_than': 3}]}, 1, SUCCESS),
    ({'any_of': [{'be_less_than': 2}, {'be_greater_than': 3}]}, 2, UNSTABLE),
    ({'any_of': [{'be_less_than': 2}, {'be_greater_than': 3}]}, 3, UNSTABLE),
    ({'any_of': [{'be_less_than': 2}, {'be_greater_than': 3}]}, 4, SUCCESS),
    ('anything', None, SUCCESS),
    ('anything', 1, SUCCESS),
    ('anything', [1], SUCCESS),
    ('anything', {'key': 'value'}, SUCCESS),
])
def test_verification(obj, verified, expected_status):
    assert match(compile_matcher(obj), verified).status == expected_status


@mark.parametrize(('obj', 'expected_value', 'expected_factory'), [
    ({'be_before': NOW.replace(tzinfo=None)}, NOW, before),
    ({'be_after': NOW}, NOW, after),
])
def test_verification_with_datetime(
    mocker,
    obj,
    expected_value,
    expected_factory,
):
    matcher_ctor = mocker.patch(f'{PKG}.ValueMatcher')
    matcher_ctor.return_value = sentinel.matcher
    value_ctor = mocker.patch(f'{PKG}.StaticValue')
    value_ctor.return_value = sentinel.value
    datetime_ctor = mocker.patch(f'{PKG}.DatetimeWithFormat')
    datetime_ctor.return_value = sentinel.datetime

    actual = compile_matcher(obj)
    assert actual == sentinel.matcher

    datetime_ctor.assert_called_once_with(expected_value)
    value_ctor.assert_called_once_with(sentinel.datetime)
    matcher_ctor.assert_called_once_with(expected_factory, sentinel.value)


@mark.parametrize(('obj', 'expected_value', 'expected_factory'), [
    ({'be_before': 'now'}, timedelta(), before),
    ({'be_after': '1 second'}, timedelta(seconds=1), after),
])
def test_verification_with_timedelta(
    mocker,
    obj,
    expected_value,
    expected_factory,
):
    matcher_ctor = mocker.patch(f'{PKG}.ValueMatcher')
    matcher_ctor.return_value = sentinel.matcher
    value_ctor = mocker.patch(f'{PKG}.RelativeDatetime')
    value_ctor.return_value = sentinel.value

    actual = compile_matcher(obj)
    assert actual == sentinel.matcher

    value_ctor.assert_called_once_with(expected_value)
    matcher_ctor.assert_called_once_with(expected_factory, sentinel.value)
