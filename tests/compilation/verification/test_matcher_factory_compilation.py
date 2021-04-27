from datetime import datetime, time, timedelta, timezone
from unittest.mock import sentinel

from pytest import fixture, mark, raises

from preacher.compilation.error import CompilationError
from preacher.compilation.verification.matcher import MatcherFactoryCompiler
from preacher.compilation.verification.matcher import add_default_matchers
from preacher.core.verification.hamcrest import after, before

PKG = 'preacher.compilation.verification.matcher'
NOW = datetime(2020, 5, 16, 12, 34, 56, tzinfo=timezone.utc)


@fixture
def compiler():
    compiler = MatcherFactoryCompiler()
    add_default_matchers(compiler)
    return compiler


@mark.parametrize('obj', [
    {},
    {'key1': 'value1', 'key2': 'value2'},
])
def test_invalid_mapping(compiler, obj):
    with raises(CompilationError):
        compiler.compile(obj)


@mark.parametrize(('obj', 'item', 'expected'), [
    ('_undefined_string', 1, False),
    ('_undefined_string', 'value', False),
    ('_undefined_string', '_undefined_string', True),
    ({'_undefined_key': 'value'}, None, False),
    ({'_undefined_key': 'value'}, 0, False),
    ({'_undefined_key': 'value'}, 'value', False),
    ({'_undefined_key': 'value'}, {'key': 'value'}, False),
    ({'_undefined_key': 'value'}, {'_undefined_key': '_'}, False),
    ({'_undefined_key': 'value'}, {'_undefined_key': 'value'}, True),
    ({'be': 1}, 0, False),
    ({'be': 1}, '1', False),
    ({'be': 1}, 1, True),
    ('be_null', None, True),
    ('be_null', False, False),
    ('not_be_null', None, False),
    ('not_be_null', False, True),
    ('be_empty', None, False),
    ('be_empty', 0, False),
    ('be_empty', '', True),
    ('be_empty', 'A', False),
    ('be_empty', [], True),
    ('be_empty', [0], False),
    ({'have_length': 1}, None, False),
    ({'have_length': 1}, 1, False),
    ({'have_length': 1}, '', False),
    ({'have_length': 1}, [], False),
    ({'have_length': {'be_less_than': 1}}, [0], False),
    ({'have_length': 1}, 'A', True),
    ({'have_length': 1}, [0], True),
    ({'have_length': {'be_less_than': 2}}, [0], True),
    ({'have_length': None}, [0], False),  # HACK: should be FAILURE
    ({'have_length': '1'}, [0], False),  # HACK: should be FAILURE
    ({'equal': 1}, 0, False),
    ({'equal': 1}, 1, True),
    ({'equal': 1}, '1', False),
    ({'be_greater_than': 0}, -1, False),
    ({'be_greater_than': 0}, 0, False),
    ({'be_greater_than': 0}, 1, True),
    ({'be_greater_than_or_equal_to': 0}, -1, False),
    ({'be_greater_than_or_equal_to': 0}, 0, True),
    ({'be_greater_than_or_equal_to': 0}, 1, True),
    ({'be_less_than': 0}, -1, True),
    ({'be_less_than': 0}, 0, False),
    ({'be_less_than': 0}, 1, False),
    ({'be_less_than_or_equal_to': 0}, -1, True),
    ({'be_less_than_or_equal_to': 0}, 0, True),
    ({'be_less_than_or_equal_to': 0}, 1, False),
    ({'contain_string': '0'}, 0, False),
    ({'contain_string': '0'}, '123', False),
    ({'contain_string': '0'}, '21012', True),
    ({'start_with': 'AB'}, 0, False),
    ({'start_with': 'AB'}, 'ABC', True),
    ({'start_with': 'AB'}, 'CAB', False),
    ({'end_with': 'BC'}, 0, False),
    ({'end_with': 'BC'}, 'ABC', True),
    ({'end_with': 'BC'}, 'BCA', False),
    ({'match_regexp': '^A*B$'}, 'ACB', False),
    ({'match_regexp': '^A*B$'}, 'B', True),
    ({'have_item': {'equal': 1}}, None, False),
    ({'have_item': {'equal': 1}}, [], False),
    ({'have_item': {'equal': 1}}, [0, 'A'], False),
    ({'have_item': {'equal': 1}}, [0, 1, 2], True),
    ({'have_items': [1, {'be_greater_than': 2}, {'be_less_than': 3}]}, [], False),
    ({'have_items': [1, {'be_greater_than': 2}, {'be_less_than': 3}]}, [1], False),
    ({'have_items': [1, {'be_greater_than': 2}, {'be_less_than': 3}]}, [1, 2, 4], True),
    ({'have_items': [1, {'be_greater_than': 2}, {'be_less_than': 3}]}, [4, 1, 2], True),
    ({'have_items': [1, {'be_greater_than': 2}, {'be_less_than': 3}]}, [1, 4, 2], True),
    ({'have_items': [1, {'be_greater_than': 2}, {'be_less_than': 3}]}, [1, 4, 2, 3], True),
    ({'contain_exactly': 1}, [], False),
    ({'contain_exactly': 1}, [1], True),
    ({'contain_exactly': 1}, [1, 2], False),
    ({'contain_exactly': 1}, [2, 3], False),
    ({'contain_exactly': [1, {'be_greater_than': 2}, {'be_less_than': 3}]}, [], False),
    ({'contain_exactly': [1, {'be_greater_than': 2}, {'be_less_than': 3}]}, [1], False),
    ({'contain_exactly': [1, {'be_greater_than': 2}, {'be_less_than': 3}]}, [1, 2, 4], False),
    ({'contain_exactly': [1, {'be_greater_than': 2}, {'be_less_than': 3}]}, [1, 4, 2], True),
    ({'contain_exactly': [1, {'be_greater_than': 2}, {'be_less_than': 3}]}, [1, 4, 2, 3], False),
    ({'contain_in_any_order': [1, {'be_greater_than': 2}, {'be_less_than': 3}]}, [], False),
    ({'contain_in_any_order': [1, {'be_greater_than': 2}, {'be_less_than': 3}]}, [1], False),
    ({'contain_in_any_order': [1, {'be_greater_than': 2}, {'be_less_than': 3}]}, [1, 2, 4], True),
    ({'contain_in_any_order': [1, {'be_greater_than': 2}, {'be_less_than': 3}]}, [4, 1, 2], True),
    ({'contain_in_any_order': [1, {'be_greater_than': 2}, {'be_less_than': 3}]}, [1, 4, 2], True),
    ({'contain_in_any_order': [1, {'be_greater_than': 2}]}, [1, 2, 4], False),
    ({'not': 1}, 'A', True),
    ({'not': 1}, 0, True),
    ({'not': 1}, 1, False),
    ({'not': {'be_greater_than': 0}}, -1, True),
    ({'not': {'be_greater_than': 0}}, 0, True),
    ({'not': {'be_greater_than': 0}}, 1, False),
    ({'all_of': []}, None, True),
    ({'all_of': [{'be_greater_than': 1}, {'be_less_than': 3}]}, 1, False),
    ({'all_of': [{'be_greater_than': 1}, {'be_less_than': 3}]}, 2, True),
    ({'all_of': [{'be_greater_than': 1}, {'be_less_than': 3}]}, 3, False),
    ({'any_of': []}, None, False),
    ({'any_of': [{'be_less_than': 2}, {'be_greater_than': 3}]}, 1, True),
    ({'any_of': [{'be_less_than': 2}, {'be_greater_than': 3}]}, 2, False),
    ({'any_of': [{'be_less_than': 2}, {'be_greater_than': 3}]}, 3, False),
    ({'any_of': [{'be_less_than': 2}, {'be_greater_than': 3}]}, 4, True),
    ('anything', None, True),
    ('anything', 1, True),
    ('anything', [1], True),
    ('anything', {'key': 'value'}, True),
])
def test_matcher_matchers(compiler, obj, item, expected):
    factory = compiler.compile(obj)
    matcher = factory.create()
    assert matcher.matches(item) == expected


@mark.parametrize('obj', [
    {'be_before': None},
    {'be_before': 0},
    {'be_after': 'XYZ'},
])
def test_matcher_compilation_failure(compiler, obj):
    with raises(CompilationError):
        compiler.compile(obj)


@mark.parametrize('obj', [
    {'contain_string': 0},
    {'start_with': 0},
    {'end_with': 0},
    {'match_regexp': 0},
])
def test_matcher_creation_failure(compiler, obj):
    factory = compiler.compile(obj)
    with raises(TypeError):
        factory.create()


@mark.parametrize(('obj', 'item'), [
    ({'match_regexp': '^A*B$'}, 0),  # HACK: should not fail.
])
def test_matcher_matching_failure(compiler, obj, item):
    factory = compiler.compile(obj)
    matcher = factory.create()
    with raises(TypeError):
        matcher.matches(item)


@mark.parametrize(('obj', 'expected_value', 'expected_func'), [
    ({'be_before': NOW.replace(tzinfo=None)}, NOW, before),
    ({'be_after': NOW}, NOW, after),
])
def test_verification_with_datetime(compiler, mocker, obj, expected_value, expected_func):
    matcher_ctor = mocker.patch(f'{PKG}.ValueMatcherFactory', return_value=sentinel.matcher)
    value_ctor = mocker.patch(f'{PKG}.StaticValue', return_value=sentinel.value)
    datetime_ctor = mocker.patch(f'{PKG}.DatetimeWithFormat', return_value=sentinel.datetime)
    mocker.patch(f'{PKG}.system_timezone', return_value=timezone.utc)

    actual = compiler.compile(obj)
    assert actual == sentinel.matcher

    datetime_ctor.assert_called_once_with(expected_value)
    value_ctor.assert_called_once_with(sentinel.datetime)
    matcher_ctor.assert_called_once_with(expected_func, sentinel.value)


@mark.parametrize(('obj', 'expected_value', 'expected_func'), [
    ({'be_before': '12:34'}, time(12, 34, tzinfo=timezone.utc), before),
    ({'be_after': '01:02+09:00'}, time(1, 2, tzinfo=timezone(timedelta(hours=9), 'JST')), after),
])
def test_verification_with_time(compiler, mocker, obj, expected_value, expected_func):
    matcher_ctor = mocker.patch(f'{PKG}.ValueMatcherFactory', return_value=sentinel.matcher)
    dt_ctor = mocker.patch(f'{PKG}.OnlyTimeDatetime', return_value=sentinel.dt)
    value_ctor = mocker.patch(f'{PKG}.DatetimeValueWithFormat', return_value=sentinel.value)
    mocker.patch('preacher.compilation.datetime.system_timezone', return_value=timezone.utc)

    actual = compiler.compile(obj)
    assert actual == sentinel.matcher

    dt_ctor.assert_called_once_with(expected_value)
    value_ctor.assert_called_once_with(sentinel.dt)
    matcher_ctor.assert_called_once_with(expected_func, sentinel.value)


@mark.parametrize(('obj', 'expected_value', 'expected_func'), [
    ({'be_before': 'now'}, timedelta(), before),
    ({'be_after': '1 second'}, timedelta(seconds=1), after),
])
def test_verification_with_timedelta(compiler, mocker, obj, expected_value, expected_func):
    matcher_ctor = mocker.patch(f'{PKG}.ValueMatcherFactory', return_value=sentinel.matcher)
    dt_ctor = mocker.patch(f'{PKG}.RelativeDatetime', return_value=sentinel.dt)
    value_ctor = mocker.patch(f'{PKG}.DatetimeValueWithFormat', return_value=sentinel.value)
    mocker.patch(f'{PKG}.system_timezone', return_value=timezone.utc)

    actual = compiler.compile(obj)
    assert actual == sentinel.matcher

    dt_ctor.assert_called_once_with(expected_value)
    value_ctor.assert_called_once_with(sentinel.dt)
    matcher_ctor.assert_called_once_with(expected_func, sentinel.value)
